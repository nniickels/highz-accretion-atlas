# Identity and crossmatch data

`v1/`, `v2/`, and `v3/` mirror the three dataset scopes. Each contains
measurement-to-object links, object-to-host links, aliases, and review/audit
tables. The v3 tables are the final complete identity products.

Some source-review inputs still carry historical internal filenames because
the ingestion code treats them as immutable audit evidence; those names do not
define additional dataset versions.
