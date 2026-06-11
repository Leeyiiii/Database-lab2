-- ============================================
-- 学籍管理系统 - 数据库初始化 DDL
-- 数据库名称: student_management
-- MySQL 8.0
-- ============================================

CREATE DATABASE IF NOT EXISTS student_management
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE student_management;

-- ============================================
-- 1. 专业表 (Major)
-- ============================================
DROP TABLE IF EXISTS Major;
CREATE TABLE Major (
    major_id    VARCHAR(20) PRIMARY KEY COMMENT '专业编号',
    major_name  VARCHAR(100) NOT NULL COMMENT '专业名称',
    department  VARCHAR(100) NOT NULL COMMENT '所属院系',
    duration    INT DEFAULT 4 COMMENT '学制（年）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业表';

-- ============================================
-- 2. 学生表 (Student)
-- ============================================
DROP TABLE IF EXISTS Student;
CREATE TABLE Student (
    student_id       VARCHAR(20) PRIMARY KEY COMMENT '学号',
    name             VARCHAR(50) NOT NULL COMMENT '姓名',
    gender           ENUM('男','女') NOT NULL COMMENT '性别',
    birth_date       DATE COMMENT '出生日期',
    id_card          VARCHAR(18) UNIQUE COMMENT '身份证号',
    native_place     VARCHAR(100) COMMENT '籍贯',
    ethnicity        VARCHAR(50) COMMENT '民族',
    political_status VARCHAR(50) COMMENT '政治面貌',
    phone            VARCHAR(20) COMMENT '联系电话',
    email            VARCHAR(100) COMMENT '邮箱',
    home_address     VARCHAR(255) COMMENT '家庭地址',
    photo_path       VARCHAR(255) COMMENT '照片存储路径',
    resume_path      VARCHAR(255) COMMENT '简历存储路径',
    enrollment_date  DATE COMMENT '入学日期',
    major_id         VARCHAR(20) COMMENT '当前专业ID',
    is_deleted       TINYINT(1) DEFAULT 0 COMMENT '软删除标记 0=正常 1=已删除',
    FOREIGN KEY (major_id) REFERENCES Major(major_id)
        ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';

-- ============================================
-- 3. 专业变更记录表 (MajorChange)
-- ============================================
DROP TABLE IF EXISTS MajorChange;
CREATE TABLE MajorChange (
    change_id     INT AUTO_INCREMENT PRIMARY KEY COMMENT '变更ID',
    student_id    VARCHAR(20) NOT NULL COMMENT '学号',
    old_major_id  VARCHAR(20) COMMENT '原专业ID',
    new_major_id  VARCHAR(20) NOT NULL COMMENT '新专业ID',
    change_date   DATE NOT NULL COMMENT '变更日期',
    reason        TEXT COMMENT '变更原因',
    status        ENUM('待审批','已通过','已驳回') DEFAULT '待审批' COMMENT '审批状态',
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (old_major_id) REFERENCES Major(major_id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (new_major_id) REFERENCES Major(major_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业变更记录表';

-- ============================================
-- 4. 奖惩记录表 (RewardPunish)
-- ============================================
DROP TABLE IF EXISTS RewardPunish;
CREATE TABLE RewardPunish (
    record_id      INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    student_id     VARCHAR(20) NOT NULL COMMENT '学号',
    type           ENUM('奖励','惩罚') NOT NULL COMMENT '类型',
    name           VARCHAR(200) NOT NULL COMMENT '奖惩名称',
    description    TEXT COMMENT '描述',
    date           DATE NOT NULL COMMENT '奖惩日期',
    evidence_path  VARCHAR(500) COMMENT '证明材料路径（支持多文件，逗号分隔）',
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='奖惩记录表';

-- ============================================
-- 5. 课程表 (Course)
-- ============================================
DROP TABLE IF EXISTS Course;
CREATE TABLE Course (
    course_id      VARCHAR(20) PRIMARY KEY COMMENT '课程编号',
    course_name    VARCHAR(100) NOT NULL COMMENT '课程名称',
    credits        DECIMAL(3,1) NOT NULL COMMENT '学分',
    hours          INT NOT NULL COMMENT '总学时',
    course_type    ENUM('必修','选修','公选') NOT NULL COMMENT '课程类型',
    semester       VARCHAR(20) COMMENT '开课学期',
    teacher        VARCHAR(50) COMMENT '授课教师',
    syllabus_path  VARCHAR(255) COMMENT '教学大纲文件路径',
    material_path  VARCHAR(500) COMMENT '教学资料路径（多文件逗号分隔）',
    description    TEXT COMMENT '课程描述/备注'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程表';

-- ============================================
-- 6. 选课记录表 (Enrollment)
-- ============================================
DROP TABLE IF EXISTS Enrollment;
CREATE TABLE Enrollment (
    enrollment_id  INT AUTO_INCREMENT PRIMARY KEY COMMENT '选课ID',
    student_id     VARCHAR(20) NOT NULL COMMENT '学号',
    course_id      VARCHAR(20) NOT NULL COMMENT '课程编号',
    semester       VARCHAR(20) NOT NULL COMMENT '选课学期',
    UNIQUE KEY uk_student_course_sem (student_id, course_id, semester),
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='选课记录表';

-- ============================================
-- 7. 成绩表 (Score)
-- ============================================
DROP TABLE IF EXISTS Score;
CREATE TABLE Score (
    score_id       INT AUTO_INCREMENT PRIMARY KEY COMMENT '成绩ID',
    enrollment_id  INT NOT NULL UNIQUE COMMENT '选课ID（一对一）',
    usual_score    DECIMAL(5,2) DEFAULT 0 COMMENT '平时成绩',
    final_score    DECIMAL(5,2) DEFAULT 0 COMMENT '期末成绩',
    total_score    DECIMAL(5,2) DEFAULT 0 COMMENT '总评成绩 = 平时*0.4 + 期末*0.6',
    FOREIGN KEY (enrollment_id) REFERENCES Enrollment(enrollment_id)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成绩表';

-- ============================================
-- 8. 管理员表 (Admin)
-- ============================================
DROP TABLE IF EXISTS Admin;
CREATE TABLE Admin (
    admin_id      INT AUTO_INCREMENT PRIMARY KEY COMMENT '管理员ID',
    username      VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希值',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';