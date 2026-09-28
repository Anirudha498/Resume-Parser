import { useState } from "react";



function App() {

  const [file,setFile] = useState(null);
  const [data,setData] = useState(null);
  const [jobDesc, setJobDesc] = useState("");

 const uploadResume = async () => {

  if(!file){
    alert("Please select a resume file");
    return;
  }

  const allowedTypes = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];

  if(!allowedTypes.includes(file.type)){
    alert("Only PDF and DOCX files are allowed");
    return;
  }

  if(file.size > 2 * 1024 * 1024){
    alert("File size should be less than 2MB");
    return;
  }

  const formData = new FormData();
  formData.append("resume",file);
  formData.append("job_desc", jobDesc);

  const res = await fetch("http://127.0.0.1:5000/upload",{
    method:"POST",
    body:formData
  });

  const result = await res.json();
  console.log("API Response:", result);
  setData(result);
}

  return (

    <div className="container">

      <div className="upload-section">

        <p>Drag & Drop Your Resume</p>
        <p>or</p>

        {/* <h2>Upload Resume</h2> */}

        <input
           type="file"
           accept=".pdf,.docx"
           onChange={(e)=>setFile(e.target.files[0])}
           
        />
        
          <p>Supported formats: PDF, DOCX | Max Size: 2MB</p>
        <br/>

        <textarea
        placeholder="Enter Job Description"
        onChange={(e)=>setJobDesc(e.target.value)}
        ></textarea>
        

        <button onClick={uploadResume} className="textcolor">
          Upload Resume
        </button><br>
        
        </br>
        

      </div>

      {data && (

        <div className="result">

          <h3>Name: {data.name}</h3>
          <p>Email: {data.email}</p>
          <p>Phone: {data.phone}</p>

          <h3>Skills</h3>

          <ul>
            {data.skills?.map((skill,i)=>(
              <li key={i}>{skill}</li>
            ))}
          </ul>
          {/* <h3>Missing Skills</h3>

              <ul>
                 {data.skill_gap?.map((skill,i)=>(
                 <li key={i}>{skill}</li>
               ))}
            </ul>
            <h3>Job Match Score</h3>
            <p>{data.match_score}%</p> */}

          <h3>Experience</h3>
          <p>{data.experience}</p>

          <h3>Projects</h3>
          <p>{data.projects}</p>

          <h3>Education</h3>
          <p>{data.education}</p>

          <h3>Match Score</h3>
          <p>{data.match_score}%</p>

          <h3>Job Required Skills</h3>

          <ul>
            {data.job_skills && data.job_skills.length > 0 ? (
            data.job_skills.map((skill, i) => (
            <li key={i}>{skill}</li>
            ))
            ) : (
            <p>No job skills found</p>
            )}
        </ul>

          <h3>Skill Gap</h3>

          <ul>
            {data.skill_gap && data.skill_gap.length > 0 ? (
             data.skill_gap.map((skill, i) => (
             <li key={i}>{skill}</li>
            ))
           ) : (
           <p>No skill gap 🎉</p>
              )}
          </ul>

        </div>

      )}

    </div>
  );
}

export default App;