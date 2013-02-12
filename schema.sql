drop table if exists app_user;
create table app_user (
    id integer primary key autoincrement,
    username string not null,
    password string not null,
    api_key string not null
);
drop table if exists todo;
create table todo (
    id integer primary key autoincrement,
    app_user integer,
    text string not null,
    done boolean not null default false,
    priority string not null default 'low',
    FOREIGN KEY(app_user) REFERENCES app_user(id)
)
