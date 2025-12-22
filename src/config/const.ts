export const LANGUAGES = {
  "zh-CN": "简体中文",
  "en-US": "English",
} as const;

export const ProcessState = {
  OUT: "已淘汰",
  PROCESSING: "进行中",
  PASS: "已通过",
  OVER: "已结束",
} as const;

export const ProcessStateEN = {
  OUT: "OUT",
  PROCESSING: "ONGOING",
  PASS: "PASS",
  OVER: "OVER",
  ABANDONED: "ABANDONED",
} as const;

export enum GROUP {
  WEB = "Web",
  GAME = "Game",
  LAB = "Lab",
  AI = "AI",
  IOS = "iOS",
  ANDROID = "Android",
  MOBILE = "Mobile",
  PM = "PM",
  DESIGN = "Design",
  BLOCKCHAIN = "Blockchain",
}

export const Group = {
  web: GROUP.WEB,
  lab: GROUP.LAB,
  ai: GROUP.AI,
  game: GROUP.GAME,
  pm: GROUP.PM,
  android: GROUP.ANDROID,
  ios: GROUP.IOS,
  design: GROUP.DESIGN,
  mobile: GROUP.MOBILE,
  blockchain: GROUP.BLOCKCHAIN,
};

export const GroupGroup = [[GROUP.WEB, GROUP.LAB, GROUP.AI, GROUP.GAME, GROUP.PM, GROUP.DESIGN, GROUP.MOBILE], [GROUP.BLOCKCHAIN]];

export const DeprecatedGroups = ["android", "ios"];

export const Step = {
  SignUp: "报名",
  WrittenTest: "笔试/问卷",
  GroupTimeSelection: "组面时间选择",
  GroupInterview: "组面",
  StressTest: "熬测",
  TeamTimeSelection: "群面时间选择",
  TeamInterview: "群面",
  Pass: "通过",
} as const;

export const StepEn = {
  SignUp: "Sign Up",
  WrittenTest: "Written Test",
  GroupTimeSelection: "Group Interview Time Selection",
  GroupInterview: "Group Interview",
  StressTest: "Stress Test",
  TeamTimeSelection: "Team Interview Time Selection",
  TeamInterview: "Team Interview",
  Pass: "Pass",
} as const;

export const Period = {
  morning: "上午",
  afternoon: "下午",
  evening: "晚上",
};

export const PeriodEn = {
  morning: "morning",
  afternoon: "afternoon",
  evening: "evening",
};

export const InterviewPlace = {
  web: "811",
  lab: "810",
  ai: "810",
  game: "808",
  pm: "809",
  android: "808",
  ios: "808",
  mobile: "808",
  design: "809",
};

export const RecruitmentNameEn = {
  A: "Fall Recruitment",
  C: "Summer Camp",
  S: "Spring Recruitment",
};

export const RecruitmentName = {
  A: "秋季招新",
  S: "春季招新",
  C: "夏令营招新",
};

export const GRADE = ["大一", "大二", "大三", "大四", "研究生"] as const;

export const GRADE_EN = [
  "Freshman",
  "Sophomore",
  "Junior",
  "Senior",
  "Graduate",
] as const;

export const RANK = ["暂无", "10%", "25%", "50%", "100%"] as const;

export const RANK_EN = ["None yet", "10%", "25%", "50%", "100%"] as const;

export const GENDERS = ["男", "女", "其他"] as const;

export const GENDERS_EN = ["male", "female", "other"] as const;


export const TIMELINE_EN = Object.values(StepEn).map((value) => {
  const res = {
    name: value,
    show: true,
  };
  res.name = value;
  if (
    value === "Group Interview Time Selection" ||
    value === "Team Interview Time Selection"
  ) {
    res.show = false;
  }
  return res;
});

export const TIMELINE = Object.values(Step).map((value) => {
  const res = {
    name: value,
    show: true,
  };
  res.name = value;
  if (value === "组面时间选择" || value === "群面时间选择") {
    res.show = false;
  }
  return res;
});

export const AVATARS = [
  "/INTJ.svg",
  "/INTP.svg",
  "/ENTJ.svg",
  "/ENTP.svg",
  "/INFJ.svg",
  "/INFP.svg",
  "/ENFJ.svg",
  "/ENFP.svg",
  "/ISTJ.svg",
  "/ISFJ.svg",
  "/ESTJ.svg",
  "/ESFJ.svg",
  "/ISTP.svg",
  "/ISFP.svg",
  "/ESTP.svg",
  "/ESFP.svg",
];

export const NecessaryInfoTitle = {
  grade: "年级",
  institute: "学院",
  major: "专业",
  rank: "加权",
  group: "意向组别",
  groups: "意向组别",
  intro: "自我介绍",
} as const;

export const NecessaryInfoTitleEn = {
  grade: "grade",
  institute: "college",
  major: "major",
  rank: "rank",
  group: "intention group",
  groups: "intention groups",
  intro: "Self introduction",
} as const;
