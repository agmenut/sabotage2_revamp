

create table if not exists portal.articles (
  id serial primary key,
  author varchar(255),
  title  varchar(255),
  has_image boolean,
  content  text,
  datestamp timestamp,
  slug varchar(30)
 );

CREATE TABLE IF NOT EXISTS users.userinfo(
    userid serial primary key,
    username varchar(32),
    email  varchar(254),
    fullname  varchar(64),
    registration_date timestamp,
    residence varchar(64),
    password_hash  char(128),
    picture_url  varchar(250),
    avatar_url  varchar(250),
    signature  varchar(250),
    quota integer default 0,
    disk_used integer default 0,
    last integer not null default 0,
    fk_groupid smallint,
    regcode varchar(8),
    active boolean default false,
    moderator integer ARRAY,
    administrator boolean default false
    );
