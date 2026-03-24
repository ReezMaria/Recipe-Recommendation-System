-- Add sample users
INSERT INTO users (username, password) VALUES ('alice', 'pass123');
INSERT INTO users (username, password) VALUES ('bob', 'pass123');

-- Add sample recipes
INSERT INTO recipes (recipe_name, description)
VALUES ('Pasta', 'Delicious pasta with tomato sauce');
INSERT INTO recipes (recipe_name, description)
VALUES ('Pancakes', 'Fluffy pancakes with syrup');

-- Add sample ingredients
INSERT INTO ingredients (ingredient_name) VALUES ('Tomato');
INSERT INTO ingredients (ingredient_name) VALUES ('Flour');
INSERT INTO ingredients (ingredient_name) VALUES ('Egg');

-- Link recipes and ingredients
INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (15, 10); -- Pasta uses Tomato
INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (16, 11); -- Pancakes use Flour
INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (16, 12); -- Pancakes use Egg

-- Add sample favorites
INSERT INTO favorites (user_id, recipe_id) VALUES (7, 16);
INSERT INTO favorites (user_id, recipe_id) VALUES (8, 15);

-- Add sample reviews
INSERT INTO reviews (user_id, recipe_id, rating, "comment")
VALUES (7, 15, 5, 'Loved it!');
INSERT INTO reviews (user_id, recipe_id, rating, "comment")
VALUES (8, 16, 4, 'Pretty good!');

-- Add step-by-step instructions for each recipe

-- Pasta Recipe Steps
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (15, 1, 'Boil water in a large pot.');
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (15, 2, 'Add pasta and cook until tender.');
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (15, 3, 'In a pan, heat tomato sauce and season with salt and herbs.');
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (15, 4, 'Drain pasta and mix with sauce.');
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (15, 5, 'Serve hot with grated cheese on top.');

-- Pancakes Recipe Steps
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (16, 1, 'Mix flour, eggs, and milk in a bowl until smooth.');
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (16, 2, 'Heat a pan and grease it lightly.');
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (16, 3, 'Pour batter onto the pan and cook until bubbles form.');
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (16, 4, 'Flip and cook the other side until golden brown.');
INSERT INTO recipe_steps (recipe_id, step_number, step_description)
VALUES (16, 5, 'Serve warm with butter and syrup.');
