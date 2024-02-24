use crate::{
    execute::{looper::TaskVariablesList, postaction::execute_command},
    inquire::inspect,
    report::{logging::log_message, webhook::notify_webhook},
    ERROR, INFO, WARNING,
};
use bollard::container::RestartContainerOptions;

pub async fn execute_tasks(var: TaskVariablesList) {
    // Prepare reusable objects
    let hostname = var.hostname;
    let docker = var.docker;
    let name = var.name;
    let id = var.id;
    let inspection: inspect::Result = var.inspection;
    let apprise_url = var.apprise_url;
    let webhook_key = var.webhook_key;
    let webhook_url = var.webhook_url;
    let post_action = var.post_action;
    let stop_timeout = var.stop_timeout;
    let restart_enable = var.restart_enable;

    // Report unhealthy container
    let msg0 = format!(
        "[{}] Container ({}) is unhealthy with {} failures",
        name, id, inspection.failing_streak
    );
    log_message(&msg0, WARNING).await;
    let msg1 = format!(
        "[{}] Container ({}) last output: [{}] {}",
        name, id, inspection.exit_code, inspection.failing_reason
    );
    log_message(&msg1, WARNING).await;

    let mut msg = "".to_string();
    if restart_enable {
        // Build restart options
        let restart_options = Some(RestartContainerOptions { t: stop_timeout });

        // Report container restarting
        let msg2 = format!(
            "[{}] Restarting container ({}) with {}s timeout",
            name, id, stop_timeout
        );
        log_message(&msg2, WARNING).await;

        // Restart unhealthy container
        let target = match id.is_empty() {
            true => name.clone(),
            false => id.clone(),
        };
        msg = match &docker.restart_container(&target, restart_options).await {
            Ok(()) => {
                // Log result
                let msg0 = format!("[{}] Restart of container ({}) was successful", name, id);
                log_message(&msg0, INFO).await;
                msg0
            }
            Err(e) => {
                // Log result
                let msg0 = format!("[{}] Restart of container ({}) failed: {}", name, id, e);
                log_message(&msg0, ERROR).await;
                msg0
            }
        };
        // Execute post-action
        if !post_action.is_empty() {
            execute_command(post_action, &name, id.to_string(), stop_timeout.to_string()).await;
        }
    }
    // Send webhook
    if !(webhook_url.is_empty() || webhook_key.is_empty()) {
        let payload = format!(
            "{{\"{}\":\"{}|{}|{}\"}}",
            &webhook_key, &hostname, &msg1, &msg
        );
        notify_webhook(&webhook_url, &payload).await;
    }
    // Send apprise
    if !apprise_url.is_empty() {
        let payload = format!(
            "{{\"title\":\"Docker-Autoheal\",\"body\":\"{}|{}|{}\"}}",
            &hostname, &msg1, &msg
        );
        notify_webhook(&apprise_url, &payload).await;
    }
}
