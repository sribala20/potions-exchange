
create table
  public.global_inventory (
    gold integer not null default 100,
    num_green_ml integer null default 0,
    num_blue_ml integer null default 0,
    num_red_ml integer null default 0,
    num_potions integer not null default 0,
    num_ml integer null default 0,
    constraint global_inventory_pkey primary key (num_potions)
  ) tablespace pg_default;

  insert into global_inventory default values


create table
  public.potions (
    sku text not null,
    name text null,
    quantity integer null default 0,
    price integer not null default 0,
    type integer[] not null,
    constraint potions_pkey primary key (sku),
    constraint potions_sku_key unique (sku)
  ) tablespace pg_default;

insert into potions (sku, price, type) 
values ('GREEN_POTION_0', 50, [0, 100, 0, 0]);

insert into potions (sku, price, type) 
values ('RED_POTION_0', 50, [100, 0, 0, 0]);

insert into potions (sku, price, type) 
values ('BLUE_POTION_0', 50, [0, 0, 100, 0]);

insert into potions (sku, price, type) 
values ('PURPLE_POTION_0', 50, [50, 0, 50, 0]);

create table
  public.carts (
    customer_name text not null,
    character_class text not null,
    level integer null,
    id integer not null,
    constraint carts_pkey primary key (id),
    constraint carts_id_key unique (id)
  ) tablespace pg_default;

create table
  public.cart_items (
    id integer not null,
    potion_sku text not null,
    quantity integer null,
    constraint cart_items_pkey primary key (id),
    constraint cart_items_id_fkey foreign key (id) references carts (id),
    constraint cart_items_potion_sku_fkey foreign key (potion_sku) references potions (sku)
  ) tablespace pg_default;