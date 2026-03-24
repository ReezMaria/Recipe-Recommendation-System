-- Search recipes by ingredient
CREATE OR REPLACE FUNCTION search_by_ingredient(p_search VARCHAR2)
RETURN SYS_REFCURSOR
IS
    rc SYS_REFCURSOR;
BEGIN
    OPEN rc FOR
    SELECT 
        r.recipe_id,
        r.recipe_name,
        r.description,
        ing.ingredients,
        steps.instructions
    FROM recipes r
    LEFT JOIN (
        SELECT ri.recipe_id,
               LISTAGG(i.ingredient_name || ' (' || ri.quantity || ')', ', ') 
               WITHIN GROUP (ORDER BY i.ingredient_name) AS ingredients
        FROM recipe_ingredients ri
        LEFT JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        GROUP BY ri.recipe_id
    ) ing ON r.recipe_id = ing.recipe_id
    LEFT JOIN (
        SELECT rs.recipe_id,
               LISTAGG(rs.step_description, CHR(10)) 
               WITHIN GROUP (ORDER BY rs.step_number) AS instructions
        FROM recipe_steps rs
        GROUP BY rs.recipe_id
    ) steps ON r.recipe_id = steps.recipe_id
    WHERE r.recipe_name LIKE '%' || p_search || '%'
       OR EXISTS (
           SELECT 1 
           FROM recipe_ingredients ri
           LEFT JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
           WHERE ri.recipe_id = r.recipe_id
             AND i.ingredient_name LIKE '%' || p_search || '%'
       );

    RETURN rc;
END;
/





CREATE OR REPLACE PROCEDURE add_favorite(
    p_user_id   IN NUMBER,
    p_recipe_id IN NUMBER
)
AS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM favorites
    WHERE user_id = p_user_id
      AND recipe_id = p_recipe_id;

    IF v_count = 0 THEN
        INSERT INTO favorites (user_id, recipe_id)
        VALUES (p_user_id, p_recipe_id);
    ELSE
        DELETE FROM favorites
        WHERE user_id = p_user_id
          AND recipe_id = p_recipe_id;
    END IF;

    COMMIT;
END;
/
