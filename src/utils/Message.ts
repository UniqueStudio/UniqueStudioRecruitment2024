import MessageComponent from "../components/public/Message.svelte";
import { mount, unmount } from "svelte";

export class Message {
	public static success(content: string) {
		const container = document.createElement("div");
		document.body.appendChild(container);
		const message = mount(MessageComponent, {
			target: container,
			props: {
				type: "success",
				content,
				onClose: () => {
					unmount(message);
					container.remove();
				}
			}
		});
	}
	public static warning(content: string) {
		const container = document.createElement("div");
		document.body.appendChild(container);
		const message = mount(MessageComponent, {
			target: container,
			props: {
				type: "warning",
				content,
				onClose: () => {
					unmount(message);
					container.remove();
				}
			}
		});
	}
	public static error(content: string) {
		const container = document.createElement("div");
		document.body.appendChild(container);
		const message = mount(MessageComponent, {
			target: container,
			props: {
				type: "error",
				content,
				onClose: () => {
					unmount(message);
					container.remove();
				}
			}
		});
	}
}
