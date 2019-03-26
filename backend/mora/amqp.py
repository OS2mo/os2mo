def publish_message(domain, action, object_type, domain_uuid):
    """Dummy function for sending AMQP messages."""
    print("[%s.%s.%s] %s" % (domain, action, object_type, domain_uuid))
