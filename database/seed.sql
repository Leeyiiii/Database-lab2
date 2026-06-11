-- ============================================
-- 学籍管理系统 - 种子数据
-- ============================================
USE student_management;

-- 管理员账号（密码明文，用于演示）
INSERT INTO Admin (username, password_hash) VALUES ('admin', 'admin123');
INSERT INTO Admin (username, password_hash) VALUES ('teacher', '123456');

-- 专业数据
INSERT INTO Major (major_id, major_name, department, duration) VALUES
('CS', '计算机科学与技术', '计算机学院', 4),
('SE', '软件工程', '计算机学院', 4),
('MATH', '数学与应用数学', '数学学院', 4),
('PHY', '物理学', '物理学院', 4);

-- 学生数据 (使用 enrollment_date)
INSERT INTO Student (student_id, name, gender, birth_date, major_id, enrollment_date, phone, email)
VALUES
('S2024001', '张三', '男', '2004-05-12', 'CS', '2024-09-01', '13800001001', 'zhangsan@example.com'),
('S2024002', '李四', '女', '2004-08-23', 'SE', '2024-09-01', '13800001002', 'lisi@example.com'),
('S2024003', '王五', '男', '2003-11-07', 'CS', '2023-09-01', '13800001003', 'wangwu@example.com');

-- 课程数据 (包含所有字段)
INSERT INTO Course (course_id, course_name, credits, hours, course_type, semester, teacher, description) VALUES
('CS101', '编译原理', 4, 64, '必修', '2025-2026-1', '刘教授', '计算机核心课程，学习编译器设计原理'),
('CS102', '数据库系统', 3, 48, '必修', '2025-2026-1', '王教授', '学习关系数据库理论与实践'),
('MATH201', '高等数学', 5, 80, '必修', '2025-2026-1', '李教授', '微积分、级数等数学基础'),
('SE301', '软件工程导论', 2, 32, '选修', '2025-2026-1', '赵教授', '软件工程基本概念与方法');

-- 选课数据
INSERT INTO Enrollment (student_id, course_id, semester) VALUES
('S2024001', 'CS101', '2025-2026-1'),
('S2024001', 'MATH201', '2025-2026-1'),
('S2024002', 'CS101', '2025-2026-1'),
('S2024002', 'MATH201', '2025-2026-1'),
('S2024003', 'CS102', '2025-2026-1');

-- 成绩数据 (触发器自动计算总评)
INSERT INTO Score (enrollment_id, usual_score, final_score) VALUES
(1, 85, 90),
(2, 78, 88),
(3, 92, 85),
(4, 70, 75),
(5, 88, 82);

SELECT 'Seed data inserted successfully.' AS status;