from pyteal import *

def approval_program():
    # Store the latest alert.
    # We will accept:
    # 1. Alert Message (string)
    # 2. Risk Score (uint64)
    # 3. Timestamp (uint64)
    # 4. Wallet Address (address, implicitly the sender)
    
    on_creation = Seq([
        App.globalPut(Bytes("TotalAlerts"), Int(0)),
        Return(Int(1))
    ])

    # Method to log alert
    # args: [ "log_alert", alert_message, risk_score, timestamp ]
    
    is_log_alert = Txn.application_args[0] == Bytes("log_alert")
    
    log_alert = Seq([
        Assert(Txn.application_args.length() == Int(4)),
        # Increment total alerts
        App.globalPut(Bytes("TotalAlerts"), App.globalGet(Bytes("TotalAlerts")) + Int(1)),
        # Emit a log event for indexers
        Log(Concat(
            Bytes("AlertLogged|"),
            Txn.application_args[1], # Message
            Bytes("|Risk:"),
            Itob(Btoi(Txn.application_args[2])), # Risk Score
            Bytes("|Time:"),
            Itob(Btoi(Txn.application_args[3])), # Timestamp
            Bytes("|By:"),
            Txn.sender()             # Sender address
        )),
        Return(Int(1))
    ])
    
    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(1))], # Allow deletion for testing
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(1))], 
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(1))],
        [Txn.on_completion() == OnComplete.CloseOut, Return(Int(1))],
        [is_log_alert, log_alert]
    )

    return program


def clear_state_program():
    return Return(Int(1))


if __name__ == "__main__":
    import os
    if not os.path.exists('build'):
        os.mkdir('build')
        
    compiled_approval = compileTeal(approval_program(), mode=Mode.Application, version=8)
    compiled_clear = compileTeal(clear_state_program(), mode=Mode.Application, version=8)
    
    with open("build/approval.teal", "w") as f:
        f.write(compiled_approval)
        
    with open("build/clear.teal", "w") as f:
        f.write(compiled_clear)
        
    print("TEAL compiled successfully to build/ directory.")
