# WhatsApp Cloud API integration checklist

1. Create a Meta developer app and add WhatsApp product.
2. Configure a WhatsApp Business Account and phone number.
3. Store phone number ID and permanent access token in deployment secrets.
4. Configure Meta webhook verification (GET challenge) and POST message subscription.
5. Point inbound messages to a secured webhook or Node-RED endpoint.
6. Parse text/list/button replies into a server-side conversation state.
7. Use approved message templates for business-initiated messages outside the 24-hour customer service window.
8. Do not assume a WhatsApp message was delivered until provider status callbacks confirm it.

The WhatsApp Cloud API is a proprietary hosted service, not an open-source component. The integration code and the rest of this project can remain open source.
