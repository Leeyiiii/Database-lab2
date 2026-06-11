-- ============================================
-- 学籍管理系统 - 事务 (Transactions)
-- ============================================

USE student_management;

-- ============================================
-- TX-01: 专业变更事务
-- 插入专业变更记录，若审批通过则同步更新学生当前专业
-- ============================================
START TRANSACTION;

    INSERT INTO MajorChange (student_id, old_major_id, new_major_id, change_date, reason, status)
    VALUES ('S2024001', 'CS', 'SE', CURDATE(), '个人兴趣转移', '已通过');

    -- 状态为“已通过”时自动同步专业（与触发器 trg_major_change_sync 互补）
    UPDATE Student SET major_id = 'SE'
    WHERE student_id = 'S2024001'
      AND (SELECT status FROM MajorChange WHERE student_id = 'S2024001' ORDER BY change_id DESC LIMIT 1) = '已通过';

COMMIT;
-- ROLLBACK;  -- 若任一操作失败，回滚全部


-- ============================================
-- TX-02: 批量成绩录入（含选课检查）
-- 若学生未选课则自动补选，随后录入成绩；失败则全部回滚
-- Example: 为 S2024002 录入两门课程成绩
-- ============================================
START TRANSACTION;

    -- 课程 1：CS101 编译原理
    INSERT INTO Enrollment (student_id, course_id, semester)
    VALUES ('S2024002', 'CS101', '2026春')
    ON DUPLICATE KEY UPDATE enrollment_id = enrollment_id;

    SET @eid1 = (SELECT enrollment_id FROM Enrollment WHERE student_id='S2024002' AND course_id='CS101' AND semester='2026春');

    INSERT INTO Score (enrollment_id, usual_score, final_score)
    VALUES (@eid1, 85, 90)
    ON DUPLICATE KEY UPDATE usual_score = 85, final_score = 90;

    -- 课程 2：MATH201 高等数学
    INSERT INTO Enrollment (student_id, course_id, semester)
    VALUES ('S2024002', 'MATH201', '2026春')
    ON DUPLICATE KEY UPDATE enrollment_id = enrollment_id;

    SET @eid2 = (SELECT enrollment_id FROM Enrollment WHERE student_id='S2024002' AND course_id='MATH201' AND semester='2026春');

    INSERT INTO Score (enrollment_id, usual_score, final_score)
    VALUES (@eid2, 78, 88)
    ON DUPLICATE KEY UPDATE usual_score = 78, final_score = 88;

COMMIT;
-- ROLLBACK;  -- 任一课程录入失败则回滚全部


-- ============================================
-- TX-03: 奖惩记录批量导入（带文件路径维护）
-- ============================================
START TRANSACTION;

    INSERT INTO RewardPunish (student_id, type, name, description, date, evidence_path)
    VALUES ('S2024003', '奖励', '校级优秀学生', '2025-2026 学年第一学期', '2025-12-15', 'uploads/evidence/excellent_cert.pdf'),
           ('S2024003', '惩罚', '旷课警告', '累计旷课 8 学时', '2026-03-20', NULL);

COMMIT;
-- ROLLBACK;  -- 任一条记录写入失败则回滚