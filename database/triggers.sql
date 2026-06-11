-- ============================================
-- 学籍管理系统 - 触发器 (Triggers)
-- ============================================

USE student_management;

-- ============================================
-- TRG-01: 成绩录入/修改时自动计算总评成绩
-- 总评 = 平时*0.4 + 期末*0.6
-- ============================================
DROP TRIGGER IF EXISTS trg_score_auto_calc;

DELIMITER //

CREATE TRIGGER trg_score_auto_calc
BEFORE INSERT ON Score
FOR EACH ROW
BEGIN
    SET NEW.total_score = NEW.usual_score * 0.4 + NEW.final_score * 0.6;
END //

DELIMITER ;


-- ============================================
-- TRG-02: 成绩更新时重新计算总评成绩
-- ============================================
DROP TRIGGER IF EXISTS trg_score_update_calc;

DELIMITER //

CREATE TRIGGER trg_score_update_calc
BEFORE UPDATE ON Score
FOR EACH ROW
BEGIN
    SET NEW.total_score = NEW.usual_score * 0.4 + NEW.final_score * 0.6;
END //

DELIMITER ;


-- ============================================
-- TRG-03: 专业变更审批通过后，自动更新学生当前专业
-- ============================================
DROP TRIGGER IF EXISTS trg_major_change_sync;

DELIMITER //

CREATE TRIGGER trg_major_change_sync
AFTER UPDATE ON MajorChange
FOR EACH ROW
BEGIN
    IF NEW.status = '已通过' AND OLD.status != '已通过' THEN
        UPDATE Student
        SET major_id = NEW.new_major_id
        WHERE student_id = NEW.student_id;
    END IF;
END //

DELIMITER ;
