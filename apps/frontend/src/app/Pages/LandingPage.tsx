import React, { useState } from "react";
import FileUpload from "../components/FileUpload";
import Chatbox from "../components/Chatbox";

export default function ChatbotPage() {
    let [isUploading, setIsUploading] = useState(false);
    return (
        <div className="grid grid-cols-12 gap-4 p-4">
                <div className="col-span-4"><FileUpload setIsUploading={setIsUploading} /></div>
                <div className="col-span-6 w-full"><Chatbox isUploading={isUploading} /></div>
        </div>
    );
}