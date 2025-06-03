CREATE_BEFORE_DELETE_ON_USER_TABLES_TRIG = """
CREATE TRIGGER sqlmate.before_delete_user_tables
BEFORE DELETE ON user_tables
FOR EACH ROW
BEGIN
	SET @table_exists = (SELECT CASE WHEN COUNT(*) = 1 THEN TRUE ELSE FALSE END
		FROM INFORMATION_SCHEMA.TABLES
		WHERE TABLE_NAME = CONCAT('u_', OLD.user_id, '_', OLD.table_name)
	);

	IF @table_exists = TRUE THEN
		INSERT INTO tables_to_drop(user_id, table_name)
		VALUES(OLD.user_id, OLD.table_name);
	END IF;
END
"""