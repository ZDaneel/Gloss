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
}

export function fetchChatAPIProcess<T = any>(params: {
  question: string;
  options: Option;
  signal?: GenericAbortSignal;
  onDownloadProgress?: (progressEvent: AxiosProgressEvent) => void;
}) {
  const chat_timeout: number = useRuntimeConfig().public.chatTimeout as number;
  let data: Record<string, any> = {
    question: params.question,
    options: params.options,
  };
  return post<T>({
    url: "/chat/chat-process",
    data,
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
  signal?: GenericAbortSignal;
}) {
  const paragraph_timeout: number = useRuntimeConfig().public
    .paragraphTimeout as number;
  let data = {
    uuid: params.uuid,
    chat_id: params.chat_id,
    paragraph_number: params.paragraph_number,
    question: params.question,
  };
  return post<T>({
    url: "/paragraphs",
    data: data,
    signal: params.signal,
    timeout: paragraph_timeout,
  });
}

export function uploadPDF<T = any>(params: { uuid?: number; file: File }) {
  const formData = new FormData();
  formData.append("file", params.file);

  const url = params.uuid
    ? `/resources/upload-pdf/${params.uuid}`
    : "/resources/upload-pdf/";

  return post<T>({
    url: url,
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}

export function uploadLink<T = any>(params: {
  uuid?: number;
  link_name: string;
}) {
  const url = params.uuid
    ? `/resources/upload-link/${params.uuid}`
    : "/resources/upload-link/";
  return post<T>({
    url: url,
    data: { link_name: params.link_name },
  });
}

export function removePDF<T = any>(params: {
  uuid: number;
  file_name: string;
}) {
  return post<T>({
    url: `/resources/remove-pdf`,
    data: params,
  });
}

export function removeLink<T = any>(params: {
  uuid: number;
  link_name: string;
}) {
  return post<T>({
    url: `/resources/remove-link`,
    data: params,
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
