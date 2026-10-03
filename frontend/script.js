// ===============================
// CareerOS Frontend
// ===============================

const API_URL = "http://127.0.0.1:8000/api";

// Student ID localStorage se milegi
let STUDENT_ID = localStorage.getItem("careerOSStudentId");

console.log("CareerOS frontend loaded 🚀");


// ===============================
// Toast
// ===============================

function showToast(message) {

    const toast = document.getElementById("toast");

    if (!toast) {
        console.log(message);
        return;
    }

    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}


// ===============================
// Load Saved Profile
// ===============================

function loadSavedProfile() {

    const savedProfile =
        localStorage.getItem("careerosProfile");

    if (!savedProfile) {
        return;
    }

    try {

        const profile =
            JSON.parse(savedProfile);

        const nameInput =
            document.getElementById("profileName");

        const roleInput =
            document.getElementById("profileRole");

        const userName =
            document.getElementById("userName");

        const avatar =
            document.getElementById("avatar");

        const targetLabel =
            document.getElementById("targetLabel");


        if (profile.name) {

            if (nameInput) {
                nameInput.value = profile.name;
            }

            if (userName) {
                userName.textContent =
                    profile.name.split(" ")[0];
            }

            if (avatar) {
                avatar.textContent =
                    profile.name
                        .charAt(0)
                        .toUpperCase();
            }
        }


        if (profile.role) {

            if (roleInput) {
                roleInput.value = profile.role;
            }

            if (targetLabel) {
                targetLabel.textContent =
                    "Target: " + profile.role;
            }
        }

    } catch (error) {

        console.error(
            "Profile loading error:",
            error
        );

    }
}


// ===============================
// Navigation
// ===============================

const navItems =
    document.querySelectorAll(
        ".nav-item[data-section]"
    );

navItems.forEach(item => {

    item.addEventListener(
        "click",
        function () {

            navItems.forEach(nav => {
                nav.classList.remove("active");
            });

            this.classList.add("active");

            const section =
                this.dataset.section;

            const element =
                document.getElementById(section);

            if (element) {

                element.scrollIntoView({
                    behavior: "smooth"
                });

            }

        }
    );

});


// ===============================
// Save Profile
// ===============================

const saveProfile =
    document.getElementById("saveProfile");

if (saveProfile) {

    saveProfile.addEventListener(
        "click",
        async function () {

            const name =
                document
                    .getElementById("profileName")
                    .value
                    .trim();

            const role =
                document
                    .getElementById("profileRole")
                    .value;


            if (!name) {

                showToast(
                    "Please enter your name"
                );

                return;
            }


            try {

                let response;


                // Existing student → UPDATE
                if (STUDENT_ID) {

                    response = await fetch(
                        `${API_URL}/students/${STUDENT_ID}`,
                        {
                            method: "PATCH",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                name: name,

                                target_role: role

                            })
                        }
                    );

                }


                // New student → CREATE
                else {

                    response = await fetch(
                        `${API_URL}/students`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({

                                name: name,

                                education: "",

                                skills: "",

                                projects: "",

                                interests: "",

                                target_role: role

                            })
                        }
                    );

                }


                if (!response.ok) {

                    throw new Error(
                        "Profile request failed"
                    );

                }


                const student =
                    await response.json();


                STUDENT_ID =
                    student.id;


                localStorage.setItem(
                    "careerOSStudentId",
                    STUDENT_ID
                );


                localStorage.setItem(
                    "careerosProfile",
                    JSON.stringify({

                        name: name,

                        role: role

                    })
                );


                document.getElementById(
                    "userName"
                ).textContent =
                    name.split(" ")[0];


                document.getElementById(
                    "avatar"
                ).textContent =
                    name
                        .charAt(0)
                        .toUpperCase();


                document.getElementById(
                    "targetLabel"
                ).textContent =
                    "Target: " + role;


                showToast(
                    "Profile saved successfully ✅"
                );


                updateProgress();

            }

            catch (error) {

                console.error(
                    "Profile error:",
                    error
                );

                showToast(
                    "Could not connect to CareerOS API"
                );

            }

        }
    );

}


// ===============================
// Resume File Selection + Upload
// ===============================

const resumeFile =
    document.getElementById("resumeFile");

if (resumeFile) {

    resumeFile.addEventListener(
        "change",
        async function () {

            const file =
                this.files[0];


            // No file
            if (!file) {

                document.getElementById(
                    "fileName"
                ).textContent =
                    "No file selected";

                return;
            }


            console.log(
                "Selected file:",
                file.name
            );


            // PDF check
            if (
                file.type !==
                    "application/pdf" &&
                !/\.pdf$/i.test(file.name)
            ) {

                showToast(
                    "Please choose a PDF resume"
                );

                this.value = "";

                return;
            }


            // 5 MB check
            if (
                file.size >
                5 * 1024 * 1024
            ) {

                showToast(
                    "Resume must be under 5 MB"
                );

                this.value = "";

                return;
            }


            // Student ID check
            if (!STUDENT_ID) {

                showToast(
                    "First save your profile"
                );

                this.value = "";

                return;
            }


            // Show file name
            document.getElementById(
                "fileName"
            ).textContent =
                file.name;


            showToast(
                "Uploading resume..."
            );


            // FormData
            const formData =
                new FormData();

            formData.append(
                "file",
                file
            );


            try {

                const response =
                    await fetch(

                        `${API_URL}/resume/upload/${STUDENT_ID}`,

                        {
                            method: "POST",
                            body: formData
                        }

                    );


                if (!response.ok) {

                    const errorText =
                        await response.text();

                    console.error(
                        "Resume API error:",
                        errorText
                    );

                    throw new Error(
                        "Resume upload failed"
                    );

                }


                const data = await response.json();

                    console.log("Resume analysis:", data);
                    console.log("FULL ANALYSIS:", JSON.stringify(data.analysis, null, 2));
                    console.log("DETECTED SKILLS:", data.analysis?.skills);
                    // Resume se detected skills Skill Coverage me show karo
                    console.log("Resume analysis:", data);

                const analysis = data.analysis || {};

                const skills =
                    analysis.skills ||
                    analysis.technical_skills ||
                    analysis.key_skills ||
                    analysis.core_skills ||
                    analysis.skills_detected ||
                    [];

                renderSkills(skills);

                document.getElementById(
                    "s-resume"
                ).className =
                    "stat-value done";


                showToast(
                    "Resume analyzed successfully ✅"
                );


                updateProgress();

            }

            catch (error) {

                console.error(
                    "Resume error:",
                    error
                );

                showToast(
                    "Resume analysis failed ❌"
                );

            }

        }
    );

}


// ===============================
// Skill Gap Analysis
// ===============================

async function runSkillGap() {

    if (!STUDENT_ID) {

        showToast(
            "First save your profile"
        );

        return;
    }


    showToast(
        "Analyzing skill gap..."
    );


    try {

        const response =
            await fetch(
                `${API_URL}/skill-gap`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        student_id: Number(STUDENT_ID),
                        target_role: document.getElementById("profileRole").value
                    })
                }
            );


        if (!response.ok) {

            const error =
                await response.text();

            console.error(
                "Skill Gap API error:",
                error
            );

            throw new Error(
                "Skill gap failed"
            );

        }


        const data =
            await response.json();


        console.log(
            "Skill Gap result:",
            data
        );


        document.getElementById(
            "s-gap"
        ).textContent =
            "Analyzed";


        document.getElementById(
            "s-gap"
        ).className =
            "stat-value done";


        showToast(
            "Skill gap analysis completed ✅"
        );


        updateProgress();

    }

    catch (error) {

        console.error(
            "Skill Gap error:",
            error
        );

        showToast(
            "Skill gap analysis failed ❌"
        );

    }

}


// ===============================
// Career Roadmap
// ===============================

async function runRoadmap() {

    if (!STUDENT_ID) {

        showToast(
            "First save your profile"
        );

        return;
    }


    showToast(
        "Generating career roadmap..."
    );


    try {

        const response =
            await fetch(
                `${API_URL}/roadmap`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        student_id: Number(STUDENT_ID),
                        target_role: document.getElementById("profileRole").value
                    })
                }
            );


        if (!response.ok) {

            const error =
                await response.text();

            console.error(
                "Roadmap API error:",
                error
            );

            throw new Error(
                "Roadmap failed"
            );

        }


        const data =
            await response.json();


        console.log(
            "Roadmap result:",
            data
        );


        document.getElementById(
            "s-road"
        ).textContent =
            "Generated";


        document.getElementById(
            "s-road"
        ).className =
            "stat-value done";


        showToast(
            "Career roadmap generated ✅"
        );


        updateProgress();

    }

    catch (error) {

        console.error(
            "Roadmap error:",
            error
        );

        showToast(
            "Roadmap generation failed ❌"
        );

    }

}


// ===============================
// Placement Intelligence
// ===============================

async function runPlacement() {

    if (!STUDENT_ID) {

        showToast(
            "First save your profile"
        );

        return;
    }


    showToast(
        "Generating placement preparation..."
    );


    try {

        const response =
            await fetch(
                `${API_URL}/placement`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        student_id: Number(STUDENT_ID),
                        target_role: document.getElementById("profileRole").value
                    })
                }
            );


        if (!response.ok) {

            const error =
                await response.text();

            console.error(
                "Placement API error:",
                error
            );

            throw new Error(
                "Placement failed"
            );

        }


        const data =
            await response.json();


        console.log(
            "Placement result:",
            data
        );


        document.getElementById(
            "s-place"
        ).textContent =
            "Ready";


        document.getElementById(
            "s-place"
        ).className =
            "stat-value done";


        showToast(
            "Placement preparation generated ✅"
        );


        updateProgress();

    }

    catch (error) {

        console.error(
            "Placement error:",
            error
        );

        showToast(
            "Placement preparation failed ❌"
        );

    }

}


// ===============================
// Module Buttons
// ===============================

const moduleButtons =
    document.querySelectorAll(
        ".module-btn"
    );

moduleButtons.forEach(button => {

    button.addEventListener(
        "click",
        function () {

            const module =
                this.dataset.module;


            if (module === "resume") {

                const resume =
                    document.getElementById(
                        "resume"
                    );

                if (resume) {

                    resume.scrollIntoView({
                        behavior:
                            "smooth"
                    });

                }

            }


            else if (
                module === "skill-gap"
            ) {

                runSkillGap();

            }


            else if (
                module === "roadmap"
            ) {

                runRoadmap();

            }


            else if (
                module === "placement"
            ) {

                runPlacement();

            }

        }
    );

});


// ===============================
// Sidebar Module Buttons
// ===============================

const moduleNav =
    document.querySelectorAll(
        ".module-nav"
    );

moduleNav.forEach(button => {

    button.addEventListener(
        "click",
        function () {

            const module =
                this.dataset.module;


            if (
                module === "skill-gap"
            ) {

                runSkillGap();

            }


            if (
                module === "roadmap"
            ) {

                runRoadmap();

            }

        }
    );

});


// ===============================
// Placement Buttons
// ===============================

const prepButtons =
    document.querySelectorAll(
        ".prep-btn"
    );

prepButtons.forEach(button => {

    button.addEventListener(
        "click",
        function () {

            runPlacement();

        }
    );

});


// ===============================
// Start Career Analysis
// ===============================

const startButton =
    document.getElementById(
        "startBtn"
    );

if (startButton) {

    startButton.addEventListener(
        "click",
        async function () {

            if (!STUDENT_ID) {

                showToast(
                    "First save your profile"
                );

                document
                    .getElementById("profile")
                    .scrollIntoView({
                        behavior: "smooth"
                    });

                return;
            }


            const resumeStatus =
                document.getElementById(
                    "s-resume"
                ).textContent;


            if (
                resumeStatus !==
                "Analyzed"
            ) {

                showToast(
                    "Upload your resume first"
                );

                document
                    .getElementById("resume")
                    .scrollIntoView({
                        behavior: "smooth"
                    });

                return;
            }


            showToast(
                "Starting CareerOS analysis..."
            );


            await runSkillGap();

            await runRoadmap();

            await runPlacement();


            showToast(
                "Career analysis completed 🚀"
            );

        }
    );

}


// ===============================
// Tour
// ===============================

const tourButton =
    document.getElementById(
        "tourBtn"
    );

if (tourButton) {

    tourButton.addEventListener(
        "click",
        function () {

            showToast(
                "CareerOS → Resume → Skill Gap → Roadmap → Placement"
            );

        }
    );

}


// ===============================
// Progress
// ===============================

function updateProgress() {

    let completed = 0;


    const resume =
        document.getElementById(
            "s-resume"
        )?.textContent;


    const gap =
        document.getElementById(
            "s-gap"
        )?.textContent;


    const roadmap =
        document.getElementById(
            "s-road"
        )?.textContent;


    const placement =
        document.getElementById(
            "s-place"
        )?.textContent;


    if (resume === "Analyzed") {
        completed++;
    }


    if (gap === "Analyzed") {
        completed++;
    }


    if (roadmap === "Generated") {
        completed++;
    }


    if (placement === "Ready") {
        completed++;
    }


    const percent =
        Math.round(
            (completed / 4) * 100
        );


    const progress =
        document.getElementById(
            "progressPercent"
        );


    if (progress) {

        progress.textContent =
            percent + "%";

    }

}


// ===============================
// Skill Bars
// ===============================

function animateBars() {

    setTimeout(() => {

        document
            .querySelectorAll(
                ".bar-fill"
            )
            .forEach(bar => {

                bar.style.width =
                    bar.dataset.width;

            });

    }, 300);

}


// ===============================
// Initialize
// ===============================

loadSavedProfile();

updateProgress();

animateBars();
function renderSkills(skills) {
    const container = document.getElementById("skill-coverage");

    if (!container) {
        console.error("Skill Coverage container not found!");
        return;
    }

    container.innerHTML = "";

    if (!skills || skills.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                No skills detected from this resume.
            </div>
        `;
        return;
    }

    // Agar skills simple strings hain:
    // ["Python", "SQL", "Java"]
    // to unhe objects mein convert karo.
    skills = skills.map((skill, index) => {
        if (typeof skill === "string") {
            return {
                name: skill,
                percentage: Math.max(50, 90 - index * 5)
            };
        }

        return {
            name: skill.name || skill.skill || skill.title || "Unknown Skill",
            percentage: Number(
                skill.percentage ??
                skill.score ??
                skill.proficiency ??
                0
            )
        };
    });

    skills.forEach(skill => {
        const row = document.createElement("div");
        row.className = "skill-row";

        row.innerHTML = `
            <div class="skill-info">
                <span>${skill.name}</span>
                <span>${skill.percentage}%</span>
            </div>

            <div class="bar">
                <div
                    class="bar-fill"
                    data-width="${skill.percentage}%"
                    style="width: 0%"
                ></div>
            </div>
        `;

        container.appendChild(row);
    });

    // Animate bars
    setTimeout(() => {
        container.querySelectorAll(".bar-fill").forEach(bar => {
            bar.style.width = bar.dataset.width;
        });
    }, 100);
}