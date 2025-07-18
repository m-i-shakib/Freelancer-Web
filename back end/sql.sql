CREATE DATABASE creative_hut_db;
CREATE USER shakib WITH PASSWORD '8052';
GRANT ALL PRIVILEGES ON DATABASE creative_hut_db TO shakib;
SELECT * FROM users;
SELECT * from gigs;
select * from users where name='samia';
select email from users where name='samia';
select description from jobs join users on jobs.buyer_id=users.id where name='hippo';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name = 'hippo';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%hippo%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%sadiaakterbonna%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%hippo%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%mahin beeva%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%mahin beeva%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%jamina begum%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%jamina begum%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%mahin beeva%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%jamina begum%';
SELECT jobs.description
FROM jobs
JOIN users ON jobs.buyer_id = users.id
WHERE users.name like '%mahin beeva%';
