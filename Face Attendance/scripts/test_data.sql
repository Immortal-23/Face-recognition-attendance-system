-- Insert test students
INSERT INTO users (id, username, email, role, created_at)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'student1', 'student1@example.com', 'student', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440001', 'student2', 'student2@example.com', 'student', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440002', 'student3', 'student3@example.com', 'student', CURRENT_TIMESTAMP);

-- Insert test attendance records
INSERT INTO attendance (student_id, status, timestamp)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'present', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440001', 'present', CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440002', 'absent', CURRENT_TIMESTAMP); 