
# Templates  
## Study

:::{dropdown} Minimal structure
:open: true
```{csv-table} 
"alias","very_unique_study"
"title", "Test Study" 
```
Download the example file <a href="_static/study-minimal.tsv" download>📥 here</a>.
:::

:::{dropdown} Extended structure
```{csv-table} 
"alias","very_unique_study"
"title", "Test Study"
"project_attribute_1","someAttribute|attributeValue"
```

```{tip}
You can add more study attributes if needed. Use the format project_attribute_{prefix}, and separate the actual attribute name and value with a | (pipe) symbol.
``` 

Download the example file <a href="_static/study-extended.tsv" download>📥 here</a>.
:::

## Sample

:::{dropdown} Minimal structure
:open: true
```{csv-table} 
:header: "alias", "geographic location (country and/or sea)", "collection date", "taxon_id"
"sample_name1", "Switzerland",	"2024-10-11", "12"
"sample_name2", "Switzerland",	"2024-10-11", "12"
"sample_name3", "Switzerland",	"2024-10-11", "12"
"sample_name4", "Switzerland",	"2024-10-11", "12"
```
Download the example file <a href="_static/sample-minimal.tsv" download>📥 here</a>.
:::

:::{dropdown} Extended structure
```{csv-table} 
:class: col-page-right
:header: "alias", "geographic location (country and/or sea)", "collection date", "taxon_id", "sex", "subject", 
"sample_name1", "Switzerland", "2024-10-11", "12", "male", "subject-1"
"sample_name2", "Switzerland", "2024-10-11", "12", "female", "subject-1"
"sample_name3", "Switzerland", "2024-10-11", "12", "male", "subject-1"
"sample_name4", "Switzerland", "2024-10-11", "12", "female", "subject-1"
```
Download the example file <a href="_static/sample-extended.tsv" download>📥 here</a>.
:::

## Experiment

:::{dropdown} Minimal structure
:open: true
The minimal number of mandatory columns for an experiment is 11. The columns `study_ref` and `sample_description` (sample ID) link each experiment to its corresponding study and sample.

Download the example file <a href="_static/experiment-minimal.tsv" download>📥 here</a>.
:::

:::{dropdown} Extended structure
Download the example files:
1. Single reads <a href="_static/experiment-extended-single-reads.tsv" download>📥 here</a>, 
2. Paired reads <a href="_static/experiment-extended-paired-reads.tsv" download>📥 here</a>.
:::
