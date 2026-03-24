CREATE OR REPLACE PROCEDURE add_recipe(
    p_name        IN VARCHAR2,
    p_desc        IN VARCHAR2,
    p_ingredients IN VARCHAR2, -- format: "Tomato:2 cups, Salt:1 tsp"
    p_steps       IN VARCHAR2  -- format: "Step1, Step2, Step3"
)
AS
    v_recipe_id   NUMBER;
    v_index       NUMBER;
    v_ing_pair    VARCHAR2(200);
    v_ingredient  VARCHAR2(100);
    v_quantity    VARCHAR2(50);
    v_step        VARCHAR2(1000);
    v_ing_id      NUMBER;
BEGIN
    -- Insert main recipe
    INSERT INTO recipes (recipe_name, description)
    VALUES (p_name, p_desc)
    RETURNING recipe_id INTO v_recipe_id;

    -- Insert ingredients (split by comma)
    FOR ingredient IN (
        SELECT REGEXP_SUBSTR(p_ingredients, '[^,]+', 1, LEVEL) AS ing_pair
        FROM dual
        CONNECT BY REGEXP_SUBSTR(p_ingredients, '[^,]+', 1, LEVEL) IS NOT NULL
    )
    LOOP
        v_ing_pair := ingredient.ing_pair;
        v_ingredient := TRIM(REGEXP_SUBSTR(v_ing_pair, '^[^:]+'));
        v_quantity   := TRIM(REGEXP_SUBSTR(v_ing_pair, '[^:]+$', 1));

        -- Handle ingredient insertion safely
        BEGIN
            SELECT ingredient_id 
            INTO v_ing_id
            FROM ingredients
            WHERE ingredient_name = v_ingredient
            AND ROWNUM = 1;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                INSERT INTO ingredients (ingredient_name)
                VALUES (v_ingredient)
                RETURNING ingredient_id INTO v_ing_id;
        END;

        -- Insert into recipe_ingredients with quantity
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity)
        VALUES (v_recipe_id, v_ing_id, v_quantity);
    END LOOP;

    -- Insert steps (split by comma)
    v_index := 1;
    FOR step_text IN (
        SELECT REGEXP_SUBSTR(p_steps, '[^,]+', 1, LEVEL) AS st
        FROM dual
        CONNECT BY REGEXP_SUBSTR(p_steps, '[^,]+', 1, LEVEL) IS NOT NULL
    )
    LOOP
        INSERT INTO recipe_steps (recipe_id, step_number, step_description)
        VALUES (v_recipe_id, v_index, TRIM(step_text.st));
        v_index := v_index + 1;
    END LOOP;

END;
/




CREATE OR REPLACE PROCEDURE add_favorite(
    p_user_id   IN NUMBER,
    p_recipe_id IN NUMBER
)
AS
    v_count NUMBER;
BEGIN
    -- Check if user already liked this recipe
    SELECT COUNT(*) INTO v_count
    FROM favorites
    WHERE user_id = p_user_id
      AND recipe_id = p_recipe_id;

    -- Only insert if not already liked
    IF v_count = 0 THEN
        INSERT INTO favorites(user_id, recipe_id)
        VALUES(p_user_id, p_recipe_id);
        COMMIT;
    END IF;

    IF v_count = 0 THEN
    INSERT INTO favorites(user_id, recipe_id) VALUES(p_user_id, p_recipe_id);
ELSE
    DELETE FROM favorites WHERE user_id = p_user_id AND recipe_id = p_recipe_id;
END IF;
COMMIT;

END;
/



CREATE OR REPLACE PROCEDURE add_review(
    p_user_id IN NUMBER,
    p_recipe_id IN NUMBER,
    p_rating IN NUMBER,
    p_review_text IN VARCHAR2
)
AS
BEGIN
    INSERT INTO reviews (user_id, recipe_id, rating, "comment")
    VALUES (p_user_id, p_recipe_id, p_rating, p_review_text);
END;
/

