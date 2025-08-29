import React, { useState, lazy, Suspense } from "react";

const FileUpload = lazy(() => import("../components/FileUpload"));
const Chatbox = lazy(() => import("../components/Chatbox"));

export default function ChatbotPage() {
    let [isUploading, setIsUploading] = useState(false);
    return (
        <Suspense fallback={<div className="p-6">Loading...</div>}>
            <div className="grid grid-cols-12 gap-4 p-4">
                <div className="col-span-4">
                    <FileUpload setIsUploading={setIsUploading} />
                </div>
                <div className="col-span-6 w-full">
                    <Chatbox isUploading={isUploading} />
                </div>
            </div>
        </Suspense>
    );
}