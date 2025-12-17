-- Unit
insert into units (name)
values ('Library & Learning Services')
on conflict (name) do nothing;

-- Strategic goals (placeholder codes; we’ll swap in the official catalog later)
insert into strategic_goals (code, title, description, category) values
 ('A1','Access & Discovery','Improve access to collections and services','A'),
 ('A2','Student Success','Support learning outcomes and retention','A'),
 ('A3','Community Engagement','Strengthen partnerships and outreach','A'),
 ('A4','Instructional Integration','Deeper integration into courses and curriculum','A'),
 ('A5','User Experience','Improve UX across platforms and spaces','A'),
 ('A6','Assessment Foundations','Build assessment practices','A'),
 ('B1','Collections','Develop and steward collections','B'),
 ('B2','Digital Scholarship','Support digital scholarship and repositories','B'),
 ('B3','Open Education','Advance OER and affordability','B'),
 ('B4','Staff Development','Grow skills and professional learning','B'),
 ('B5','Workplace Culture','Foster inclusive and healthy teams','B'),
 ('C1','Teaching Support','Partner with faculty on instruction','C'),
 ('C2','Fiscal Responsibility','Strengthen budgeting, licensing, and analytics','C'),
 ('C3','Stewardship & Infrastructure','Sustain systems, facilities, and safety','C')
on conflict (code) do nothing;

-- Teams (Team 1..2) – reference the unit row safely via SELECT
insert into teams (name, unit_id)
select 'Team 1', u.id from units u where u.name = 'Library & Learning Services'
on conflict (unit_id, name) do nothing;

insert into teams (name, unit_id)
select 'Team 2', u.id from units u where u.name = 'Library & Learning Services'
on conflict (unit_id, name) do nothing;

-- People (Person 1..3)
insert into people (name, title, unit_id)
select 'Person 1', 'Librarian', u.id from units u where u.name = 'Library & Learning Services'
on conflict (unit_id, name) do nothing;

insert into people (name, title, unit_id)
select 'Person 2', 'Coordinator', u.id from units u where u.name = 'Library & Learning Services'
on conflict (unit_id, name) do nothing;

insert into people (name, title, unit_id)
select 'Person 3', 'Analyst', u.id from units u where u.name = 'Library & Learning Services'
on conflict (unit_id, name) do nothing;

-- Team membership via joins (PK is (team_id, person_id), so ON CONFLICT works)
insert into team_members (team_id, person_id)
select t.id, p.id
from teams t
join people p on p.name in ('Person 1','Person 2')
where t.name = 'Team 1'
on conflict do nothing;

insert into team_members (team_id, person_id)
select t.id, p.id
from teams t
join people p on p.name in ('Person 3')
where t.name = 'Team 2'
on conflict do nothing;
