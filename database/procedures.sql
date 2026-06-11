-- ============================================
-- 学籍管理系统 - 存储过程 (Stored Procedures)
-- ============================================

USE student_management;

-- ============================================
-- SP-01: 计算学生 GPA
-- GPA = SUM(credits * total_score/100*4.0) / SUM(credits)
-- ============================================
DROP PROCEDURE IF EXISTS sp_calc_gpa;

DELIMITER //

CREATE PROCEDURE sp_calc_gpa(
    IN p_student_id VARCHAR(20),
    OUT p_gpa DECIMAL(4,2)
)
READS SQL DATA
BEGIN
    DECLARE total_weighted DECIMAL(10,4) DEFAULT 0;
    DECLARE total_credits DECIMAL(10,1) DEFAULT 0;

    SELECT SUM(c.credits * (sc.total_score / 100.0 * 4.0)),
           SUM(c.credits)
    INTO total_weighted, total_credits
    FROM Score sc
    JOIN Enrollment e ON sc.enrollment_id = e.enrollment_id
    JOIN Course c ON e.course_id = c.course_id
    WHERE e.student_id = p_student_id;

    IF total_credits > 0 THEN
        SET p_gpa = total_weighted / total_credits;
    ELSE
        SET p_gpa = 0;
    END IF;
END //

DELIMITER ;

-- ============================================
-- SP-02: 课程成绩排名
-- 返回指定课程的学生成绩排名表
-- ============================================
DROP PROCEDURE IF EXISTS sp_rank_by_course;

DELIMITER //

CREATE PROCEDURE sp_rank_by_course(
    IN p_course_id VARCHAR(20)
)
READS SQL DATA
BEGIN
    SELECT
        e.student_id,
        s.name AS student_name,
        sc.total_score,
        RANK() OVER (ORDER BY sc.total_score DESC) AS course_rank
    FROM Score sc
    JOIN Enrollment e ON sc.enrollment_id = e.enrollment_id
    JOIN Student s ON e.student_id = s.student_id
    WHERE e.course_id = p_course_id AND s.is_deleted = 0
    ORDER BY sc.total_score DESC;
END //

DELIMITER ;

-- ============================================
-- SP-03: 计算学生按学期 GPA
-- 参数: 学号，返回按学期分组的 GPA
-- ============================================
DROP PROCEDURE IF EXISTS sp_calc_semester_gpa;

DELIMITER //

CREATE PROCEDURE sp_calc_semester_gpa(
    IN p_student_id VARCHAR(20)
)
READS SQL DATA
BEGIN
    SELECT e.semester,
           ROUND(SUM(c.credits * (sc.total_score / 100.0 * 4.0)) / SUM(c.credits), 2) AS semester_gpa,
           SUM(c.credits) AS total_credits,
           COUNT(*) AS course_count
    FROM Score sc
    JOIN Enrollment e ON sc.enrollment_id = e.enrollment_id
    JOIN Course c ON e.course_id = c.course_id
    WHERE e.student_id = p_student_id
    GROUP BY e.semester
    ORDER BY e.semester;
END //

DELIMITER ;