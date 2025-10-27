
# Templates  
## Study

### Minimal study structure

```{csv-table} 
"alias","very_unique_study"
"title", "Test Study" 
```
Download the example file <a href="_static/study-minimal.tsv" download>📥 here</a>.


### Extended study structure

```{csv-table} 
"alias","very_unique_study"
"title", "Test Study"
"project_attribute_1","someAttribute|attributeValue"
```
:::{aside}
```{tip}
You can add more study attributes if needed. Use the format project_attribute_{prefix}, and separate the actual attribute name and value with a | (pipe) symbol.
::: 

Download the example file <a href="_static/study-extended.tsv" download>📥 here</a>.

## Sample
### Minimal sample structure
```{csv-table} 
:header: "alias", "geographic location (country and/or sea)", "collection date", "taxon_id"
"sample_name1", "Switzerland",	"2024-10-11", "12"
"sample_name2", "Switzerland",	"2024-10-11", "12"
"sample_name3", "Switzerland",	"2024-10-11", "12"
"sample_name4", "Switzerland",	"2024-10-11", "12"
```
Download the example file <a href="_static/sample-minimal.tsv" download>📥 here</a>.


### Extended sample structure

```{csv-table} 
:class: col-page-right
:header: "alias", "geographic location (country and/or sea)", "collection date", "taxon_id", "sex", "subject", 
"sample_name1", "Switzerland", "2024-10-11", "12", "male", "subject-1"
"sample_name2", "Switzerland", "2024-10-11", "12", "female", "subject-1"
"sample_name3", "Switzerland", "2024-10-11", "12", "male", "subject-1"
"sample_name4", "Switzerland", "2024-10-11", "12", "female", "subject-1"
```
Download the example file <a href="_static/sample-extended.tsv" download>📥 here</a>.

## Experiment

### Minimal experiment structure

The minimal number of mandatory columns for an experiment is 11. The columns study_ref and sample_description (sample ID) link each experiment to its corresponding study and sample.

Download the example file <a href="_static/experiment-minimal.tsv" download>📥 here</a>.

### Extended experiment structure

Download the example file <a href="_static/experiment-extended.tsv" download>📥 here</a>.
