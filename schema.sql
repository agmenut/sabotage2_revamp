create table if not exists haxorbb.article_images (
  id serial primary key,
  location varchar(255),
  title varchar(255),
  link varchar (2048)
);

create table if not exists haxorbb.articles (
  id serial primary key,
  author varchar(255),
  title  varchar(255),
  has_image boolean,
  fk_image int references article_images(id),
  content  text,
  datestamp timestamp
 );

