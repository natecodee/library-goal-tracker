select count(*) as units from units;
select count(*) as goals_catalog from strategic_goals;
select name from teams order by name;
select name, title from people order by name;
select t.name as team, p.name as member
from team_members tm
join teams t on tm.team_id = t.id
join people p on tm.person_id = p.id
order by team, member;
