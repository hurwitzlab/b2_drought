drop table if exists cv;
create table cv (
    cv_id serial primary key,
    term varchar(255) unique,
    display_name varchar(255),
    definition text,
    section varchar(50),
    units varchar(50),
    dtype varchar(50), -- enum?
    aliases varchar(50)
);
