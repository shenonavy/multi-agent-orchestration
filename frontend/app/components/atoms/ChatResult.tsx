import { Message } from "@/app/types/chat";

export default function ChatResult(props: Message) {
  const { role, content, source } = props;

  return (
    <div
      className={`flex ${role === "user" ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          role === "user"
            ? "bg-blue-500 text-white"
            : role === "system"
            ? "bg-red-500 text-white"
            : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        }`}
      >
        <p>{content}</p>
        {source && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Source: {source}
          </p>
        )}
      </div>
    </div>
  );
}
