delete FROM salman.spec_table where ATTR_NAME like '%Index%';


update spec_table set Attr_name = 'Graphics Card' where ATTR_NAME = 'Graphics';
update spec_table set Attr_name = 'RAM' where ATTR_NAME = 'Memory';
update spec_table set Attr_name = 'Warranty' where ATTR_NAME = 'Manufacturing Warranty';
update spec_table set Attr_name = 'Power Supply' where ATTR_NAME = 'Adapter';

-- delete from spec_table where PRODUCT_ID<1000;
-- delete from images where PRODUCT_ID<1000;
-- delete from products where  ID<1000;
