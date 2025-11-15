import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, SKOS, DCTERMS
import os
from pathlib import Path

# --- 1. Define Namespaces ---
# These must match the prefixes we added to Protégé
ESCO = Namespace("http://data.europa.eu/esco/model#")
DCT = Namespace("http://purl.org/dc/terms/")
# Note: SKOS, RDF, and RDFS are already built-in to rdflib

# --- 2. Set Up File Paths ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
ontology_file = os.path.join(project_root, "ontology", "toil.rdf") # Using .rdf
model_file = os.path.join(project_root, "data", "model.rdf") # We must also load the model
csv_file = os.path.join(project_root, "data", "occupations_en.csv")

# --- 3. Load the Ontology ---
print(f"Loading ontology from: {ontology_file}")
g = Graph()

# --- FIX 1: Convert paths to URIs for parsing ---
ontology_uri = Path(ontology_file).as_uri()
model_uri = Path(model_file).as_uri()

# Parse the main file (toil.rdf)
g.parse(ontology_uri, format="xml")
print(f"Base ontology loaded. Triples: {len(g)}")

# Parse the imported model (model.rdf) so the script knows the classes
print(f"Loading model from: {model_file}")
g.parse(model_uri, format="xml")
print(f"Ontology and model loaded. Total triples: {len(g)}") # <-- This count should be > 50

# --- 4. Load the CSV Data ---
print(f"Loading CSV data from: {csv_file}")
df = pd.read_csv(csv_file)
# Drop any rows where the essential URI is missing
df = df.dropna(subset=['conceptUri'])
print(f"Found {len(df)} occupations to import. (This is the correct number from your last log)")

# --- 5. Iterate and Add Triples ---
print("Starting import process...")
for index, row in df.iterrows():
    # Define the new individual (Subject)
    subject = URIRef(row['conceptUri'])
    
    # Add the triples (Predicate, Object)
    
    # --- FIX 2: Use the correct ESCO namespace for MemberConcept ---
    g.add((subject, RDF.type, ESCO.MemberConcept)) 
    
    # 2. Add Label: Add the English preferred label
    if pd.notna(row['preferredLabel']):
        g.add((subject, RDFS.label, Literal(row['preferredLabel'], lang='en')))
        
    # 3. Add Description: Add the English description
    if pd.notna(row['description']):
        g.add((subject, DCT.description, Literal(row['description'], lang='en')))
        
    # 4. Add Notation: Add the ISCO group code
    if pd.notna(row['iscoGroup']):
        g.add((subject, SKOS.notation, Literal(row['iscoGroup'])))

    # Print progress
    if (index + 1) % 1000 == 0:
        print(f"  ...processed {index + 1} rows.")

print("Import process complete.")

# --- 6. Save the New Ontology ---
print(f"Saving updated ontology back to: {ontology_file}")
g.serialize(destination=ontology_file, format="xml")

print("---")
print(f"SUCCESS! Ontology populated with {len(df)} individuals.")
print(f"You can now open {ontology_file} in Protégé.")