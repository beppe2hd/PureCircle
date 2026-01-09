
## Entity Relationship (Conceptual)

Field
 ├── SoilMoisture
 ├── Irrigation
 └── LAI

Each measurement:
- Belongs to one Field
- Is recorded at a Timestamp
- Only the SoilMoisture record is Applies to a Zone (in-line or between-lines)

## Entities & Attributes (ER Schema)

#### FIELD
- id (PK)
- crop_type
- ir_mode

#### SOIL_MOISTURE
- id (PK)
- ts
- sensor_zone (binary / boolean)
- water_content
- field_id (FK → FIELD.id)

#### IRRIGATION
- id (PK)
- ts
- water_volume
- field_id (FK → FIELD.id)

#### LAI
- id (PK)
- ts
- lai
- field_id (FK → FIELD.id)



## Cardinality Summary
| Relationship | Cardinality |
|----|---|
|FIELD → SOIL_MOISTURE	| 1 : N |
|FIELD → IRRIGATION |	1 : N |
|FIELD → LAI |	1 : N |