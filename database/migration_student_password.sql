-- ============================================
-- 数据库迁移：为已有 Student 表添加密码字段
-- 运行方式：mysql -u root -p < database/migration_student_password.sql
-- ============================================
USE student_management;

-- 步骤 1：添加密码列（如果不存在）
ALTER TABLE Student ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) DEFAULT NULL COMMENT '学生登录密码';

-- 步骤 2：为已有学生设定默认密码（学号 + "123"）
-- 仅更新 password_hash 为 NULL 的学生
UPDATE Student SET password_hash = CONCAT(student_id, '123') WHERE password_hash IS NULL;

SELECT 'Migration completed: password_hash column added and populated.' AS status;