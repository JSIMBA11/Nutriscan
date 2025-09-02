-- Create the lessons table if it doesn't exist
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

-- Seed lessons
INSERT INTO lessons (title, content) VALUES
('Balanced Plate Basics', 'Learn how to build a balanced meal: 1/2 veggies, 1/4 carbs, 1/4 protein.'),
('Food Storage 101', 'Keep dairy cold, grains dry, label leftovers with dates to reduce waste.'),
('Hydration Habits', 'Aim for regular water intake; flavored water is ok if low sugar.');