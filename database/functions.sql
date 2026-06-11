-- ============================================
-- 学籍管理系统 - 函数 (Functions)
-- ============================================

USE student_management;

-- ============================================
-- FN-01: 计算学生平均成绩
-- 参数: 学号
-- ============================================
DROP FUNCTION IF EXISTS fn_avg_score;

DELIMITER //

CREATE FUNCTION fn_avg_score(
    p_student_id VARCHAR(20)
)
RETURNS DECIMAL(5,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE avg_sc DECIMAL(5,2) DEFAULT 0;
    SELECT AVG(sc.total_score) INTO avg_sc
    FROM Score sc
    JOIN Enrollment e ON sc.enrollment_id = e.enrollment_id
    WHERE e.student_id = p_student_id;
    RETURN IFNULL(avg_sc, 0);
END //

DELIMITER ;

-- ============================================
-- FN-02: 学生已选课程数
-- 参数: 学号
-- ============================================
DROP FUNCTION IF EXISTS fn_course_count;

DELIMITER //

CREATE FUNCTION fn_course_count(
    p_student_id VARCHAR(20)
)
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE cnt INT DEFAULT 0;
    SELECT COUNT(DISTINCT e.course_id) INTO cnt
    FROM Enrollment e
    WHERE e.student_id = p_student_id;
    RETURN cnt;
END //

DELIMITER ;

-- ============================================
-- FN-03: 计算指定课程的平均成绩
-- 参数: 课程编号
-- ============================================
DROP FUNCTION IF EXISTS fn_course_avg_score;

DELIMITER //

CREATE FUNCTION fn_course_avg_score(
    p_course_id VARCHAR(20)
)
RETURNS DECIMAL(5,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE avg_sc DECIMAL(5,2) DEFAULT 0;
    SELECT AVG(sc.total_score) INTO avg_sc
    FROM Score sc
    JOIN Enrollment e ON sc.enrollment_id = e.enrollment_id
    WHERE e.course_id = p_course_id;
    RETURN IFNULL(avg_sc, 0);
END //

DELIMITER ;
