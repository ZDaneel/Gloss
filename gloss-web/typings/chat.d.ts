declare namespace Chat {
  interface Chat {
    chat_id: number;
    text: string;
    paragraphs: string[];
    dateTime: string;
    isGood?: boolean;
    isUser?: boolean;
    error?: boolean;
    loading?: boolean;
    requestOptions: { prompt: string };
  }

  interface History {
    title: string;
    isEdit: boolean;
    uuid: number;
    isFirst: boolean;
    updatedAt: string;
    temperature: number;
    contextNum: number;
    isContextUnlimited: boolean;
    tableEnhanceOpen: boolean;
    paragraphNum: number;
    paperTitle?: string;
  }

  interface ChatState {
    active: number | null;
    usingContext: boolean;
    history: History[];
    chat: { uuid: number; data: Chat[] }[];
  }

  interface ConversationResponse {
    conversationId: string;
    detail: {
      choices: {
        finish_reason: string;
        index: number;
        logprobs: any;
        text: string;
      }[];
      created: number;
      id: string;
      model: string;
      object: string;
      usage: {
        completion_tokens: number;
        prompt_tokens: number;
        total_tokens: number;
      };
    };
    id: string;
    parentMessageId: string;
    role: string;
    text: string;
  }
}

//conversationOptions?: ConversationRequest | null
//requestOptions: { prompt: string; options?: ConversationRequest | null }
