import type { AxiosProgressEvent, GenericAbortSignal } from "axios";
import { post } from "@/utils/request";
import { useRuntimeConfig } from "#imports";

interface Option {
  uuid: number;
  chat_id: number;
  temperature: number;
  past_questions: string[];
  past_answers: string[];
  paragraph_number: number;
  need_table: boolean;
  source_text: string;
}

export function fetchChatAPIProcess<T = any>(params: {
  question: string;
  options: Option;
  signal?: GenericAbortSignal;
  onDownloadProgress?: (progressEvent: AxiosProgressEvent) => void;
}) {
  const chat_timeout: number = useRuntimeConfig().public.chatTimeout as number;
  return post<T>({
    url: "/chat/chat-process",
    data: { question: params.question, options: params.options },
    signal: params.signal,
    onDownloadProgress: params.onDownloadProgress,
    timeout: chat_timeout,
  });
}

export function fetchParagraphAPI<T = any>(params: {
  uuid: number;
  chat_id: number;
  paragraph_number: number;
  question: string;
  source_text: string;
  signal?: GenericAbortSignal;
}) {
  const paragraph_timeout: number = useRuntimeConfig().public
    .paragraphTimeout as number;
  return post<T>({
    url: "/paragraphs",
    data: {
      uuid: params.uuid,
      chat_id: params.chat_id,
      paragraph_number: params.paragraph_number,
      question: params.question,
      source_text: params.source_text,
    },
    signal: params.signal,
    timeout: paragraph_timeout,
  });
}

export function uploadText<T = any>(params: { content: string }) {
  return post<T>({
    url: "/resources/upload-text/",
    data: { content: params.content },
  });
}

export function fetchLikeAPI<T = any>(params: {
  uuid: number;
  chat_id: number;
  is_good: boolean;
}) {
  return post<T>({
    url: "/chat/like",
    data: params,
  });
}
