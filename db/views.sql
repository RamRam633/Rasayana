-- GOLD serving views. Thin, read-optimized projections over the normalized model.
-- These are the surfaces the API, UI, and (read-only) text-to-SQL prefer.

-- One row per plant with a preferred vernacular name + rollup counts.
create or replace view v_plant_overview as
select
  p.id,
  p.accepted_name,
  p.family,
  p.resolution_confidence,
  p.is_curated,
  (select pn.name from plant_name pn
     where pn.plant_id = p.id and pn.name_kind = 'sanskrit'
     order by pn.is_preferred desc limit 1)                       as sanskrit_name,
  (select count(*) from plant_phytochemical x where x.plant_id = p.id) as phytochemical_count,
  (select count(*) from plant_use u where u.plant_id = p.id)          as use_count
from plant p;

-- Formulation with its ingredients and indications rolled into JSON.
create or replace view v_formulation_detail as
select
  f.id,
  f.name,
  s.code as system_code,
  f.dosage_form,
  f.classical_reference,
  f.is_curated,
  coalesce((
    select jsonb_agg(jsonb_build_object(
             'plant', pl.accepted_name,
             'ingredient_text', fi.ingredient_text,
             'part_used', fi.part_used,
             'role', fi.role,
             'source', src.short_code))
    from formulation_ingredient fi
    left join plant pl on pl.id = fi.plant_id
    left join source src on src.id = fi.source_id
    where fi.formulation_id = f.id), '[]'::jsonb)                 as ingredients,
  coalesce((
    select jsonb_agg(distinct tu.preferred_label)
    from formulation_use fu
    join therapeutic_use tu on tu.id = fu.therapeutic_use_id
    where fu.formulation_id = f.id), '[]'::jsonb)                 as indications
from formulation f
left join system s on s.id = f.system_id;

-- Lightweight search surface (id + names + family) for typeahead.
create or replace view v_plant_search as
select p.id, p.accepted_name, p.family,
       array_agg(distinct pn.name) filter (where pn.name is not null) as also_known_as
from plant p
left join plant_name pn on pn.plant_id = p.id
group by p.id, p.accepted_name, p.family;
