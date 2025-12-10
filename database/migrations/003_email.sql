CREATE TABLE email (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    transaction_id INT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(10) NOT NULL CHECK (status IN ('sent', 'failed')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
);
