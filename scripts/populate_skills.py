import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS
import os
from pathlib import Path

# --- 1. Define Namespaces ---
ESCO = Namespace("http://data.europa.eu/esco/model#")
DCT = Namespace("http://purl.org/dc/terms/")

# --- 2. Set Up File Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
ontology_file = os.path.join(project_root, "ontology", "toil.rdf") # Our main ontology
model_file = os.path.join(project_root, "data", "model.rdf")     # The ESCO model definition
csv_file = os.path.join(project_root, "data", "skills_en.csv")   # <-- Our new data source

# --- 3. Load the Ontology ---
print(f"Loading existing ontology from: {ontology_file}")
g = Graph()
ontology_uri = Path(ontology_file).as_uri()
model_uri = Path(model_file).as_uri()

g.parse(ontology_uri, format="xml")
print(f"Base ontology loaded. Triples: {len(g)}")

# Parse the imported model so the script knows the classes
# We do this again in case the main file doesn't have it (good practice)
g.parse(model_uri, format="xml")
print(f"Ontology and model loaded. Total triples: {len(g)}")

# --- 4. Load the CSV Data ---
print(f"Loading NEW CSV data from: {csv_file}")
df = pd.read_csv(csv_file)
df = df.dropna(subset=['conceptUri'])
print(f"Found {len(df)} skills to import.")

# --- 5. Iterate and Add Triples ---
print("Starting SKILLS import process...")
for index, row in df.iterrows():
    # Define the new individual (Subject)
    subject = URIRef(row['conceptUri'])
    
    # Add the triples (Predicate, Object)
    
    # 1. Add Type: This individual is an 'esco:Skill'
    g.add((subject, RDF.type, ESCO.Skill)) # <-- Using the correct, specific class
    
    # 2. Add Label: Add the English preferred label
    if pd.notna(row['preferredLabel']):
        g.add((subject, RDFS.label, Literal(row['preferredLabel'], lang='en')))
        
    # 3. Add Description: Add the English description
    if pd.notna(row['description']):
        g.add((subject, DCT.description, Literal(row['description'], lang='en')))
        
    # 4. Add Skill Type: (e.g., 'skill/competence' or 'knowledge')
    if pd.notna(row['skillType']):
        g.add((subject, ESCO.skillType, Literal(row['skillType'])))


    # Print progress
    if (index + 1) % 1000 == 0:
        print(f"  ...processed {index + 1} rows.")

print("SKILLS import process complete.")

# --- 6. Save the Updated Ontology ---
print(f"Saving updated ontology back to: {ontology_file}")
g.serialize(destination=ontology_file, format="xml")

print("---")
print(f"SUCCESS! Ontology now populated with {len(df)} new skills.")
print(f"You can now open {ontology_file} in Protégé.")