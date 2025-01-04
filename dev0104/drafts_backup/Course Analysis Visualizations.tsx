import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const sizeRanges = [
  {
    title: "소규모 강좌 (10-20명)",
    subtitle: "412개 강좌 (57.2%)",
    color: "#2563eb",
    data: [
      { name: "체력훈련5", score: 4.93, responses: 14, college: "예술체육대학" },
      { name: "전공실기5", score: 4.92, responses: 14, college: "예술체육대학" },
      { name: "스포츠지도특강", score: 4.89, responses: 10, college: "예술체육대학" },
      { name: "체육철학", score: 4.87, responses: 11, college: "예술체육대학" },
      { name: "체력훈련1", score: 4.85, responses: 13, college: "예술체육대학" },
      { name: "전공과진로1", score: 4.81, responses: 13, college: "방목기초교육대학" },
      { name: "전공실기1", score: 4.81, responses: 13, college: "예술체육대학" },
      { name: "체력훈련3", score: 4.77, responses: 12, college: "예술체육대학" },
      { name: "전공실기3", score: 4.75, responses: 13, college: "예술체육대학" },
      { name: "스포츠컨디셔닝", score: 4.75, responses: 13, college: "예술체육대학" }
    ],
    analysis: [
      "Highest scores overall (4.85-4.93)",
      "Dominated by 예술체육대학 (College of Arts and Physical Education)",
      "Mostly specialized physical education courses",
      "Shows excellence in small, practice-based classes"
    ]
  },
  {
    title: "중소규모 강좌 (21-50명)",
    subtitle: "217개 강좌 (30.1%)",
    color: "#059669",
    data: [
      { name: "국제경영전략", score: 4.72, responses: 24, college: "국제학부" },
      { name: "창의혁신리더십론", score: 4.70, responses: 25, college: "국제학부" },
      { name: "기업윤리와지속경영", score: 4.64, responses: 33, college: "국제학부" },
      { name: "인적자원개발론", score: 4.62, responses: 36, college: "국제학부" },
      { name: "한국현대문화비평", score: 4.42, responses: 23, college: "대학" },
      { name: "건축종합설계1", score: 4.42, responses: 22, college: "건축대학" },
      { name: "교양볼링", score: 4.40, responses: 48, college: "방목기초교육대학" },
      { name: "시적상상력과이미지", score: 4.38, responses: 22, college: "인문대학" },
      { name: "C++Programming", score: 4.38, responses: 26, college: "방목기초교육대학" },
      { name: "교양탁구", score: 4.37, responses: 31, college: "방목기초교육대학" }
    ],
    analysis: [
      "Very high scores (4.42-4.72)",
      "Strong showing from 국제학부 (International Studies)",
      "Focus on business and leadership courses",
      "Good balance of class size and interaction"
    ]
  },
  {
    title: "중대규모 강좌 (51-100명)",
    subtitle: "54개 강좌 (7.5%)",
    color: "#7c3aed",
    data: [
      { name: "외국인학생을위한한국문화", score: 4.33, responses: 54, college: "방목기초교육대학" },
      { name: "기초영어", score: 4.17, responses: 71, college: "방목기초교육대학" },
      { name: "외국인학생을위한한국현대사", score: 4.15, responses: 54, college: "방목기초교육대학" },
      { name: "자기경영과실전취업준비", score: 4.14, responses: 80, college: "방목기초교육대학" },
      { name: "현대사회와심리학", score: 4.10, responses: 93, college: "방목기초교육대학" },
      { name: "글로벌경영전략", score: 4.05, responses: 68, college: "대학" },
      { name: "건축학개론", score: 4.04, responses: 51, college: "방목기초교육대학" },
      { name: "기계학습", score: 4.03, responses: 59, college: "ICT융합대학" },
      { name: "민주주의와현대사회", score: 4.03, responses: 66, college: "방목기초교육대학" },
      { name: "채권총론", score: 4.01, responses: 53, college: "법과대학" }
    ],
    analysis: [
      "Solid scores (4.10-4.33)",
      "방목기초교육대학 (Bangmok College of Basic Studies) courses",
      "Notable focus on international student courses",
      "Maintains good ratings despite larger size"
    ]
  },
  {
    title: "대규모 강좌 (100명 이상)",
    subtitle: "36개 강좌 (5.0%)",
    color: "#dc2626",
    data: [
      { name: "영어회화2", score: 4.28, responses: 161, college: "방목기초교육대학" },
      { name: "C언어", score: 4.20, responses: 113, college: "방목기초교육대학" },
      { name: "미적분학1", score: 4.17, responses: 154, college: "방목기초교육대학" },
      { name: "영어회화3", score: 4.11, responses: 190, college: "방목기초교육대학" },
      { name: "영어회화1", score: 4.10, responses: 453, college: "방목기초교육대학" },
      { name: "캡스톤디자인1", score: 4.04, responses: 167, college: "공과대학" },
      { name: "발표와토의", score: 4.03, responses: 154, college: "방목기초교육대학" },
      { name: "영어1", score: 4.01, responses: 337, college: "방목기초교육대학" },
      { name: "디지털리터러시의이해", score: 3.98, responses: 101, college: "방목기초교육대학" },
      { name: "글쓰기", score: 3.97, responses: 309, college: "방목기초교육대학" }
    ],
    analysis: [
      "Still impressive scores (4.10-4.28)",
      "All from 방목기초교육대학",
      "Core curriculum courses (English, Math, Programming)",
      "Shows quality can be maintained in large classes"
    ]
  }
];

const CourseChart = ({ rangeData }) => (
  <Card className="mb-8">
    <CardHeader>
      <CardTitle className="text-2xl font-bold">{rangeData.title}</CardTitle>
      <p className="text-gray-500">{rangeData.subtitle}</p>
    </CardHeader>
    <CardContent>
      <div className="h-96 w-full">
        <ResponsiveContainer>
          <BarChart data={rangeData.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              angle={-45} 
              textAnchor="end" 
              height={120}
              interval={0}
              tick={{ fontSize: 11 }}
            />
            <YAxis 
              domain={[3, 5]} 
              ticks={[3.0, 3.5, 4.0, 4.5, 5.0]}
              label={{ value: '평균 점수', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-4 border rounded shadow-lg">
                      <p className="font-bold">{data.name}</p>
                      <p>평균 점수: {data.score.toFixed(2)}</p>
                      <p>응답자 수: {data.responses}명</p>
                      <p>단과대학: {data.college}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar 
              dataKey="score" 
              fill={rangeData.color}
              label={{ 
                position: 'top', 
                content: ({ value }) => value.toFixed(2)
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-6">
        <h3 className="text-xl font-semibold mb-4">분석</h3>
        <ul className="list-disc pl-6 space-y-2">
          {rangeData.analysis.map((point, idx) => (
            <li key={idx}>{point}</li>
          ))}
        </ul>
      </div>
    </CardContent>
  </Card>
);

const CourseAnalysis = () => {
  return (
    <div className="space-y-8 p-4">
      {sizeRanges.map((range, idx) => (
        <CourseChart key={idx} rangeData={range} />
      ))}
    </div>
  );
};

export default CourseAnalysis;