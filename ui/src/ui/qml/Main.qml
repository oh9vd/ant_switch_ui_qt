import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    width: 520
    height: 85
    visible: true
    title: appTitle
    function formatKHz(value) {
        if (!value || value <= 0) {
            return "";
        }
        return (value).toLocaleString(Qt.locale(), 'f', 0) + " kHz";
    }
    component ToggleButton: Button {
        checkable: true
        width: 37
    }

    Column {
        anchors.centerIn: parent
        spacing: 1
        width: parent.width * 0.9

        Row {
            spacing: 8
            width: parent.width

            CheckBox {
                id: cbAutoA
                text: qsTr("Auto")
                enabled: radioStatus.aFreq > 0 && !bridge.busy
                checked: bridge.autoA
                onClicked: bridge.autoA = checked
            }

            ButtonGroup {
                buttons: aRow.children
                exclusive: true
            }

            Row {
                id: aRow
                spacing: 6

                ToggleButton {
                    id: rbA0
                    text: antennaNames[0]
                    enabled: !bridge.busy
                    checked: wsStatus.a === "-"
                    onClicked: {
                        if (rbA0.checked) {
                            cbAutoA.checked = false;
                            bridge.autoA = false;
                        }
                        bridge.selectAntenna("A", 0);
                    }
                }

                ToggleButton {
                    id: rbA1
                    text: antennaNames[1]
                    enabled: !bridge.busy && !rbB1.checked && (!cbAutoA.checked || wsStatus.a === "1")
                    checked: wsStatus.a === "1"
                    onClicked: {
                        bridge.selectAntenna("A", 1);
                    }
                }

                ToggleButton {
                    id: rbA2
                    text: antennaNames[2]
                    enabled: !bridge.busy && !rbB2.checked && (!cbAutoA.checked || wsStatus.a === "2")
                    checked: wsStatus.a === "2"
                    onClicked: {
                        bridge.selectAntenna("A", 2);
                    }
                }

                ToggleButton {
                    id: rbA3
                    text: antennaNames[3]
                    enabled: !bridge.busy && !rbB3.checked && (!cbAutoA.checked || wsStatus.a === "3")
                    checked: wsStatus.a === "3"
                    onClicked: {
                        bridge.selectAntenna("A", 3);
                    }
                }

                ToggleButton {
                    id: rbA4
                    text: antennaNames[4]
                    enabled: !bridge.busy && !rbB4.checked && (!cbAutoA.checked || wsStatus.a === "4")
                    checked: wsStatus.a === "4"
                    onClicked: {
                        bridge.selectAntenna("A", 4);
                    }
                }

                ToggleButton {
                    id: rbA5
                    text: antennaNames[5]
                    enabled: !bridge.busy && !rbB5.checked && (!cbAutoA.checked || wsStatus.a === "5")
                    checked: wsStatus.a === "5"
                    onClicked: {
                        bridge.selectAntenna("A", 5);
                    }
                }

                ToggleButton {
                    id: rbA6
                    text: antennaNames[6]
                    enabled: !bridge.busy && !rbB6.checked && (!cbAutoA.checked || wsStatus.a === "6")
                    checked: wsStatus.a === "6"
                    onClicked: {
                        bridge.selectAntenna("A", 6);
                    }
                }
            }

            Label {
                id: lblRigA
                text: rigAName
                font.bold: true
                horizontalAlignment: Text.AlignLeft
                width: 40
            }

            Label {
                id: lblRigAFreq
                text: formatKHz(radioStatus.aFreq)
                horizontalAlignment: Text.AlignLeft
            }
        }

        Row {
            spacing: 8
            width: parent.width

            CheckBox {
                id: cbAutoB
                text: qsTr("Auto")
                enabled: radioStatus.bFreq > 0 && !bridge.busy
                checked: bridge.autoB
                onClicked: bridge.autoB = checked
            }

            ButtonGroup {
                buttons: bRow.children
                exclusive: true
            }

            Row {
                id: bRow
                spacing: 6

                ToggleButton {
                    id: rbB0
                    text: antennaNames[0]
                    enabled: !bridge.busy
                    checked: wsStatus.b === "-"
                    onClicked: {
                        if (rbB0.checked) {
                            cbAutoB.checked = false;
                            bridge.autoB = false;
                        }
                        bridge.selectAntenna("B", 0);
                    }
                }

                ToggleButton {
                    id: rbB1
                    text: antennaNames[1]
                    enabled: !bridge.busy && !rbA1.checked && (!cbAutoB.checked || wsStatus.b === "1")
                    checked: wsStatus.b === "1"
                    onClicked: {
                        bridge.selectAntenna("B", 1);
                    }
                }

                ToggleButton {
                    id: rbB2
                    text: antennaNames[2]
                    enabled: !bridge.busy && !rbA2.checked && (!cbAutoB.checked || wsStatus.b === "2")
                    checked: wsStatus.b === "2"
                    onClicked: {
                        bridge.selectAntenna("B", 2);
                    }
                }

                ToggleButton {
                    id: rbB3
                    text: antennaNames[3]
                    enabled: !bridge.busy && !rbA3.checked && (!cbAutoB.checked || wsStatus.b === "3")
                    checked: wsStatus.b === "3"
                    onClicked: {
                        bridge.selectAntenna("B", 3);
                    }
                }

                ToggleButton {
                    id: rbB4
                    text: antennaNames[4]
                    enabled: !bridge.busy && !rbA4.checked && (!cbAutoB.checked || wsStatus.b === "4")
                    checked: wsStatus.b === "4"
                    onClicked: {
                        bridge.selectAntenna("B", 4);
                    }
                }

                ToggleButton {
                    id: rbB5
                    text: antennaNames[5]
                    enabled: !bridge.busy && !rbA5.checked && (!cbAutoB.checked || wsStatus.b === "5")
                    checked: wsStatus.b === "5"
                    onClicked: {
                        bridge.selectAntenna("B", 5);
                    }
                }

                ToggleButton {
                    id: rbB6
                    text: antennaNames[6]
                    enabled: !bridge.busy && !rbA6.checked && (!cbAutoB.checked || wsStatus.b === "6")
                    checked: wsStatus.b === "6"
                    onClicked: {
                        bridge.selectAntenna("B", 6);
                    }
                }
            }

            Label {
                id: lblRigB
                text: rigBName
                horizontalAlignment: Text.AlignLeft
                width: 40
                font.bold: true
            }

            Label {
                id: lblRigBFreq
                text: formatKHz(radioStatus.bFreq)
                horizontalAlignment: Text.AlignLeft
                width: 40
            }
        }
    }
    footer: ToolBar {
        height: 20
        RowLayout {
            spacing: 8
            width: parent.width * 0.9
            Label {
                id: lblStatus
                text: bridge.statusMessage
                leftPadding: 8
            }
            Label {
                id: lblVersion
                text: "Version " + appVersion
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignRight
            }
        }
    }
}
