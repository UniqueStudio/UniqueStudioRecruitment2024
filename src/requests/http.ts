/* eslint-disable @typescript-eslint/no-explicit-any */

interface ResponseType<T> {
  code: number;
  data: T;
  msg: string;
}

export interface FetcherOptions extends Partial<RequestInit> {
  prefix?: string;
  apiEndpoint?: string;
}

export class Http {
  private apiEndpoint?: string;
  private prefix?: string;
  private fetchOptions?: Partial<RequestInit>;
  constructor(options?: FetcherOptions) {
    const { apiEndpoint, prefix, ...initOptions } = options ?? {};
    this.apiEndpoint = apiEndpoint ?? import.meta.env.VITE_API_ENDPOINT;
    this.prefix = prefix ?? ""; //maybe dev
    this.fetchOptions = initOptions;
  }

  private concatUrl = (path: string) =>
    `${this.apiEndpoint}${this.prefix}${path}`;

  private generateParams = (url: string, params: Record<string, any>) => {
    const paramsArr: string[] = [];
    Object.keys(params).forEach((key) => {
      const value = typeof params[key] === "undefined" ? "" : params[key];
      paramsArr.push([key, encodeURIComponent(value)].join("="));
    });
    return `${url}?${paramsArr.join("&")}`;
  };
  private mergeOptions = (
    method: string,
    data?: Record<string, any> | FormData,
    options?: RequestInit
  ) => {
    const result = {
      method,
      credentials: "include" as const,
      ...(this.fetchOptions
        ? Object.assign(this.fetchOptions, options)
        : options),
    };
    if (data) {
      result.body = data instanceof FormData ? data : JSON.stringify(data);
    }
    return result;
  };

  private async parseFetch<T>(res: Response) {
    if (!res.ok) {
      const detail = (await res.json()) as ResponseType<null>;
      if(detail.msg === "authentication failed could not get uid") {
        // 调试模式不跳转，方便调试
        if (import.meta.env.MODE!=="development"){
          window.location.href = "https://sso2024.hustunique.com/login?from=join2024.hustunique.com";
        }else{
          console.error("登录错误，请手动设置 cookie,示例： document.cookie=\"SSO_SESSION=你的cookie\"");
        }
      }
      throw new Error(detail.msg);
    }
    try {
      const parseResult = (await res.json()) as ResponseType<T>;
      return parseResult;
    } catch (err) {
      throw new Error("response with no body");
    }
  }

  async get<T>(
    path: string,
    data?: Record<string, any>,
    options?: RequestInit
  ) {
    return await this.parseFetch<T>(
      await fetch(
        data
          ? this.generateParams(this.concatUrl(path), data)
          : this.concatUrl(path),
        this.mergeOptions("GET", options)
      )
    );
  }

  async getRaw(
    path: string,
    data?: Record<string, any>,
    options?: RequestInit
  ) {
    return await fetch(
      data
        ? this.generateParams(this.concatUrl(path), data)
        : this.concatUrl(path),
      this.mergeOptions("GET", options)
    );
  }

  async post<T>(
    path: string,
    data?: Record<string, any>,
    options?: RequestInit
  ) {
    return await this.parseFetch<T>(
      await fetch(
        this.concatUrl(path),
        this.mergeOptions("POST", data, options)
      )
    );
  }

  async postRaw(
    path: string,
    data?: Record<string, any>,
    options?: RequestInit
  ) {
    return await fetch(
      this.concatUrl(path),
      this.mergeOptions("POST", data, options)
    );
  }

  async postFormData<T>(path: string, data: FormData) {
    return await this.parseFetch<T>(
      await fetch(
        this.concatUrl(path),
        this.mergeOptions("POST", data, {
          headers: {
            credentials: "include",
          },
        })
      )
    );
  }

  async put<T>(
    path: string,
    data?: Record<string, any> | FormData,
    options?: RequestInit
  ) {
    return await this.parseFetch<T>(
      await fetch(this.concatUrl(path), this.mergeOptions("PUT", data, data instanceof FormData ? {
        headers: {
          credentials: "include",
        },
      } :options))
    );
  }



  async delete<T>(
    path: string,
    data: Record<string, any>,
    options?: RequestInit
  ) {
    return await this.parseFetch<T>(
      await fetch(
        this.concatUrl(path),
        this.mergeOptions("DELETE", data, options)
      )
    );
  }
}

export const http = new Http({
  prefix: "",
  apiEndpoint: import.meta.env.VITE_HR_DOMAIN_BE,
  headers: {
    "Content-Type": "application/json",
    accept: "application/json, text/plain, */*"
  },
});
