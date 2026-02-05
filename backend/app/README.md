# Domain Model

### Entities
- User
- Workspace
- Source
- Artifacts


### Relationship
- User uploads audio -> source (stored in s3)
- Transcribe audio into text -> artifact (transcript)
- GPT summarizes transcript -> artifact (summary)
- GPT formulates actionable items -> artifact (action_items)

### Useful links
- SQLAlchemy ORM docs - https://docs.sqlalchemy.org/en/21/orm/
