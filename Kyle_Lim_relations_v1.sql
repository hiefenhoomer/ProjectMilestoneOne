-- Dropped all tables in the database for testing.
DO $$
DECLARE 
    r RECORD;
BEGIN 
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP 
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE'; 
    END LOOP; 
END $$;

create table "attributes" (
	"attribute" varchar(50) primary key,
	value varchar(20) not null
);

create table categories (
	category varchar(50) primary key
);

create table zipcode (
	zipcode char(5) primary key,
	population int,
	avg_income int
);

create table business (
	business_id varchar(100) primary key,
	name varchar(100) not null,
	address varchar(200) not null,
	city varchar(100) not null,
	state varchar(100) not null,
	zipcode char(5) not null,
	longititude decimal(3,7),
	latitude decimal(3,7),
	isOpen int,
	stars decimal(1,1)	
);

create table BusinessCategories (
	fk_business_id varchar(100) not null,
	fk_category varchar(50) not null,
	primary key (fk_business_id, fk_category),
	foreign key (fk_business_id) references business(business_id),
	foreign key (fk_category) references categories(category)
);

create table BusinessAttributes (
	fk_business_id varchar(100),
	fk_attribute varchar(50) not null,
	primary key (fk_business_id, fk_attribute),
	foreign key (fk_business_id) references business(business_id),
	foreign key (fk_attribute) references Attributes(attribute)
);

create table checkin ( 
	fk_business_id varchar(100),
	day varchar(10) not null,
	hour varchar(20) not null,
	count int,
	primary key (fk_business_id, day, hour),
	foreign key (fk_business_id) references business(business_id)
);

create table yelp_user (
	user_id varchar(100) primary key,
	name varchar(100) not null,
	yelping_since date,
	review_count int,
	fans int,
	average_stars decimal(3,2),
	funny int,
	cool int
);

create table friend (
	user_id varchar(100) not null,
	friend_id varchar(100) not null,
	foreign key (user_id) references yelp_user(user_id),
	foreign key (friend_id) references yelp_user(user_id)
);

create view avg_income_global as
-- Collapse all incomes in zipcode on avg_income.
select
	avg(avg_income) as avg_income_global
from
	zipcode;

create view global_income_business as
select
	b.business_id,
	b.name,
	b.zipcode,
	z.avg_income,
	g.avg_income_global,
	-- get the income difference.
	(z.avg_income - g.avg_income_global) as income_difference
from 
	business b
join
	zipcode z 
on
-- join on same zipcode.
	b.zipcode = z.zipcode
-- Have to cross join here so every column has the global average associated with it.
cross join 
	avg_income_global g;

 
-- Overpriced is this: 
-- $: - Not overpriced 
-- $$ - Overpriced if zip average is < global average - 5000 
-- $$$ - overpriced if zip avg < global avg + 5000
create view is_overpriced as
select
	gb.business_id, gb.name, gb.zipcode, gb.avg_income, gb.avg_income_global, gb.income_difference,
	a.value as price_rating,
	-- If else statements end as var means var = aggregate of conditionals
	case
		when a.value = '3' and gb.income_difference > 5000 then 'no'
		when a.value = '2' and gb.income_difference > -5000 then 'no'
		when a.value = '1' then 'no'
		else 'yes' end as overpriced 
	from
		global_income_business gb
	join
	-- Get the many to many relationship.
		businessAttributes ba on gb.business_id = ba.fk_business_id
	join 
		"attributes" a on ba.fk_attribute = a."attribute"
	where 
		a."attribute" = 'RestaurantsPriceRange2';
	

-- View helper to show all the businesses.
create view show_business_checkins as
	select
		ch.fk_business_id, b.name, sum(ch.count) as total_checkins
	from
		checkin ch
	join
		business b on b.business_id = ch.fk_business_id
	group by
		ch.fk_business_id,
		b.name;

-- Sort all businesses into popularity.
create view popular_businesses as
	select
		b.business_id, b.name, bc.total_checkins, b.zipcode, 
		row_number() over (partition by b.zipcode order by bc.total_checkins desc) as rank
	from 
		show_business_checkins bc
	join
		business b on b.business_id = bc.fk_business_id;

-- Get the get the top 10 popular businesses per zip for better representation.
create view top_10_popular_businesses_per_zip as
	select 
		business_id,
		name,
		zipcode,
		total_checkins
	from
		popular_businesses
	where 
		rank <= 10;

-- Helper view
create view business_total_checkins_days_count as
	select
		b.business_id, b.name, b.zipcode, sum(ch.count) as total_checkins, count(distinct ch.day) as total_days
	from 
		checkin ch
	join
		business b on b.business_id = ch.fk_business_id
	group by 
		b.business_id,
		b.name,
		b.zipcode;

-- Successful businesses are defined as businesses with the highest daily customers.
-- The top 10 are taken from every zip
create view top_10_successful_bussinesses_per_zip as
with business_daily_customers as (
	select
		business_id, avg_ch.name, 
		avg_ch.zipcode, 
		(avg_ch.total_checkins / avg_ch.total_days) as avg_daily_customers,
		row_number() over (partition by avg_ch.zipcode order by (avg_ch.total_checkins / avg_ch.total_days) desc) as rank
	from business_total_checkins_days_count avg_ch
)
select
	business_id,
	name,
	zipcode,
	avg_daily_customers
from
	business_daily_customers
where 
	rank <= 10
	
	