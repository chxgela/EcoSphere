INSERT INTO users (firstname, lastname, contact, email)
VALUES ('Jonna', 'Fresado', '09550957912', 'jonnaf07@gmail.com');

INSERT INTO transactions (user_id, amount, mode_of_payment, transaction_number, reference_number)
VALUES (21, 500, 'Maya', 'TXN0005783421', 'ECO-111532462');

INSERT INTO email (user_id, transaction_id, sent_at, status)
VALUES (21, 21, NOW(), 'sent');

UPDATE users 
SET contact = '09922346892'
WHERE id = 1;

UPDATE transactions
SET amount = 7765
WHERE id = 5;

UPDATE email
SET status = 'failed'
WHERE id = 21;

DELETE FROM users
WHERE id = 16;

DELETE FROM transactions
WHERE id = 2;
