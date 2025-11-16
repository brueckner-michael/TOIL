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
csv_file = os.path.join(project_root, "data", "occupationSkillRelations_en.csv")   # <-- Our final data source

# --- 3. Load the Ontology ---
print(f"Loading existing ontology from: {ontology_file}")
g = Graph()
ontology_uri = Path(ontology_file).as_uri()
model_uri = Path(model_file).as_uri()

g.parse(ontology_uri, format="xml")
print(f"Base ontology loaded. Triples: {len(g)}")

# Parse the imported model so the script knows the classes
g.parse(model_uri, format="xml")
print(f"Ontology and model loaded. Total triples: {len(g)}")

# --- 4. Load the CSV Data ---
print(f"Loading NEW CSV data from: {csv_file}")
df = pd.read_csv(csv_file)
# We need both the occupation and the skill URI to create a relation
df = df.dropna(subset=['occupationUri', 'skillUri']) 
print(f"Found {len(df)} occupation-skill relations to import.")

# --- 5. Iterate and Add Triples ---
print("Starting RELATIONS import process...")
for index, row in df.iterrows():
    # Define the Subject (Occupation) and Object (Skill)
    subject = URIRef(row['occupationUri'])
    obj = URIRef(row['skillUri'])
    
    # Add the relationship (Predicate)
    
    # We will assume for this import that all relations in this file
    # are 'essential' skills. This is the most common use.
    g.add((subject, ESCO.hasEssentialSkill, obj)) 

    # Print progress
    if (index + 1) % 10000 == 0: # This file is large, so log every 10k
        print(f"  ...processed {index + 1} relations.")

print("RELATIONS import process complete.")

# --- 6. Save the Updated Ontology ---
print(f"Saving updated ontology back to: {ontology_file}")
g.serialize(destination=ontology_file, format="xml")

print("---")
print(f"SUCCESS! Ontology now populated with {len(df)} new relations.")
print(f"You can now open {ontology_file} in Protégé.")