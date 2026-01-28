const API_BASE = "http://127.0.0.1:8000/api";

const uploadForm = document.getElementById("upload-form");
const recordBtn = document.getElementById("record-btn");
const recordStatus = document.getElementById("record-status");
const lectureListEl = document.getElementById("lecture-list");

const detailEmptyEl = document.getElementById("lecture-detail-empty");
const detailEl = document.getElementById("lecture-detail");
const detailTitleEl = document.getElementById("detail-title");
const detailMetaEl = document.getElementById("detail-meta");
const detailStatusEl = document.getElementById("detail-status");
const detailTranscriptEl = document.getElementById("detail-transcript");
const detailNotesEl = document.getElementById("detail-notes");

const generateNotesBtn = document.getElementById("generate-notes-btn");
const exportPdfBtn = document.getElementById("export-pdf-btn");
const exportTxtBtn = document.getElementById("export-txt-btn");

let currentLectureId = null;
let mediaRecorder = null;
let recordedChunks = [];
let isRecording = false;

function mapStatusToLabel(status) {
  const s = status.toUpperCase();
  if (s === "COMPLETED") return { text: "Completed", cls: "completed" };
  if (s === "TRANSCRIBING" || s === "TRANSCRIBED" || s === "GENERATING_NOTES") {
    return { text: s.replace("_", " ").toLowerCase(), cls: "generating_notes" };
  }
  if (s === "ERROR") return { text: "Error", cls: "error" };
  return { text: "Uploaded", cls: "transcribing" };
}

async function fetchLectures() {
  try {
    const res = await fetch(`${API_BASE}/lectures`);
    if (!res.ok) throw new Error("Failed to fetch lectures");
    const lectures = await res.json();
    renderLectureList(lectures);
  } catch (err) {
    console.error(err);
  }
}

function renderLectureList(lectures) {
  lectureListEl.innerHTML = "";
  if (!Array.isArray(lectures) || lectures.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No lectures yet. Upload or record an audio file.";
    li.className = "lecture-meta";
    lectureListEl.appendChild(li);
    return;
  }

  lectures.forEach((lecture) => {
    const li = document.createElement("li");
    li.className = "lecture-item";
    li.dataset.id = lecture.id;

    const left = document.createElement("div");
    const titleEl = document.createElement("div");
    titleEl.className = "lecture-title";
    titleEl.textContent = lecture.title;
    const metaEl = document.createElement("div");
    metaEl.className = "lecture-meta";
    const parts = [];
    if (lecture.course) parts.push(lecture.course);
    if (lecture.lecturer) parts.push(lecture.lecturer);
    if (lecture.lecture_date) parts.push(lecture.lecture_date);
    metaEl.textContent = parts.join(" • ");
    left.appendChild(titleEl);
    left.appendChild(metaEl);

    const right = document.createElement("div");
    const statusSpan = document.createElement("span");
    const statusInfo = mapStatusToLabel(lecture.status);
    statusSpan.className = `status-pill ${statusInfo.cls}`;
    statusSpan.textContent = statusInfo.text;
    right.appendChild(statusSpan);

    // Add delete button
    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-btn";
    deleteBtn.innerHTML = "❌";
    deleteBtn.title = "Delete lecture";
    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // Prevent triggering the lecture selection
      deleteLecture(lecture.id, lecture.title);
    });
    right.appendChild(deleteBtn);

    li.appendChild(left);
    li.appendChild(right);

    li.addEventListener("click", () => {
      document
        .querySelectorAll(".lecture-item")
        .forEach((el) => el.classList.remove("active"));
      li.classList.add("active");
      showLectureDetail(lecture.id);
    });

    lectureListEl.appendChild(li);
  });
}

async function showLectureDetail(lectureId) {
  currentLectureId = lectureId;
  try {
    const res = await fetch(`${API_BASE}/lectures/${lectureId}`);
    if (!res.ok) throw new Error("Failed to fetch lecture details");
    const lecture = await res.json();

    detailEmptyEl.classList.add("hidden");
    detailEl.classList.remove("hidden");

    detailTitleEl.textContent = lecture.title;

    const metaParts = [];
    if (lecture.course) metaParts.push(lecture.course);
    if (lecture.lecturer) metaParts.push(lecture.lecturer);
    if (lecture.lecture_date) metaParts.push(lecture.lecture_date);
    detailMetaEl.textContent = metaParts.join(" • ");

    const statusInfo = mapStatusToLabel(lecture.status);
    detailStatusEl.textContent = `Status: ${statusInfo.text}`;

    detailTranscriptEl.textContent =
      lecture.transcript_text || "Transcript not available.";
    detailNotesEl.textContent = lecture.notes_text || "Notes not generated yet.";
  } catch (err) {
    console.error(err);
    alert("Failed to load lecture details.");
  }
}

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData();
  const title = uploadForm.title.value.trim();
  if (!title) {
    alert("Title is required.");
    return;
  }

  formData.append("title", title);
  formData.append("course", uploadForm.course.value.trim());
  formData.append("lecturer", uploadForm.lecturer.value.trim());
  formData.append("lecture_date", uploadForm.lecture_date.value);

  const fileInput = uploadForm.audio_file;

  if (fileInput.files.length > 0) {
    formData.append("audio_file", fileInput.files[0]);
  } else if (recordedChunks.length > 0) {
    const blob = new Blob(recordedChunks, { type: "audio/webm" });
    formData.append("audio_file", blob, "recording.webm");
  } else {
    alert("Please select an audio file or record from microphone.");
    return;
  }

  const submitBtn = document.getElementById("upload-submit");
  submitBtn.disabled = true;
  submitBtn.textContent = "Uploading & Transcribing...";

  try {
    const res = await fetch(`${API_BASE}/lectures`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Upload failed");
    }
    await res.json();

    recordedChunks = [];
    fileInput.value = "";

    await fetchLectures();
    alert("Lecture uploaded and transcribed successfully.");
  } catch (err) {
    console.error(err);
    alert("Upload or transcription failed. Check backend logs.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Upload & Transcribe";
  }
});

recordBtn.addEventListener("click", async () => {
  if (!isRecording) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      recordedChunks = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          recordedChunks.push(e.data);
        }
      };
      mediaRecorder.onstop = () => {
        recordStatus.textContent = "Recording stopped. Ready to upload.";
      };

      mediaRecorder.start();
      isRecording = true;
      recordBtn.textContent = "Stop Recording";
      recordStatus.textContent = "Recording...";
    } catch (err) {
      console.error(err);
      alert("Unable to access microphone.");
    }
  } else {
    mediaRecorder.stop();
    isRecording = false;
    recordBtn.textContent = "Start Recording";
  }
});

generateNotesBtn.addEventListener("click", async () => {
  if (!currentLectureId) return;
  generateNotesBtn.disabled = true;
  generateNotesBtn.textContent = "Generating...";
  try {
    const res = await fetch(`${API_BASE}/lectures/${currentLectureId}/generate-notes`, {
      method: "POST",
    });
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Failed to generate notes");
    }
    const data = await res.json();
    detailNotesEl.textContent = data.notes_text;
    await fetchLectures();
  } catch (err) {
    console.error(err);
    alert("Failed to generate notes. Ensure Ollama is running with the model loaded.");
  } finally {
    generateNotesBtn.disabled = false;
    generateNotesBtn.textContent = "Generate Notes";
  }
});

async function downloadFile(url, filename) {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Download failed");
    const blob = await res.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(link.href);
  } catch (err) {
    console.error(err);
    alert("Download failed.");
  }
}

exportPdfBtn.addEventListener("click", async () => {
  if (!currentLectureId) return;
  await downloadFile(
    `${API_BASE}/lectures/${currentLectureId}/export?format=pdf`,
    "lecture_notes.pdf"
  );
});

exportTxtBtn.addEventListener("click", async () => {
  if (!currentLectureId) return;
  await downloadFile(
    `${API_BASE}/lectures/${currentLectureId}/export?format=txt`,
    "lecture_notes.txt"
  );
});

async function deleteLecture(lectureId, lectureTitle) {
  if (!confirm(`Are you sure you want to delete "${lectureTitle}"? This cannot be undone.`)) {
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/lectures/${lectureId}`, {
      method: "DELETE",
    });
    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || "Delete failed");
    }

    // If the deleted lecture is currently selected, hide the detail view
    if (currentLectureId === lectureId) {
      currentLectureId = null;
      detailEl.classList.add("hidden");
      detailEmptyEl.classList.remove("hidden");
    }

    await fetchLectures();
    alert("Lecture deleted successfully.");
  } catch (err) {
    console.error(err);
    alert("Failed to delete lecture.");
  }
}

fetchLectures();

