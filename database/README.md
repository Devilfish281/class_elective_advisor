WEB Site: https://catalog.fullerton.edu/preview_program.php?catoid=91&poid=42762&returnto=13411

colleges.csv
college_id,name
1,College of the Arts
2,College of Business and Economics
...

departments.csv
department_id,college_id,name
1,1,Art Department
2,1,Music School
...

degree_levels.csv
degree_level_id,department_id,name
1,1,Bachelor�s
2,1,Master�s
3,1,Minor
...

degrees.csv
degree_id,degree_level_id,name
1,1,Art History, B.A.
2,1,Art, Ceramics Concentration, B.F.A.
...

requirements.csv
requirement_id,degree_id,type,name
1,25,Core,Computer Science Core
...

subcategories.csv
subcategory_id,requirement_id,name
1,1,Lower-Division Core
2,1,Upper-Division Core
...

courses.csv
course_id,subcategory_id,name,description,prerequisites
1,1,CPSC 120, Introduction to Programming, (3),
2,1,CPSC 121, Object-Oriented Programming, (3),
3,5,CPSC 254, Software Development with Open Source Systems, Philosophy of open source software development..., CPSC 131
...
