import os
import tempfile

import pyblish.api
import ftrack
import pymel


class TGBVFXMayaRepairScene(pyblish.api.Action):

    label = "Repair"
    icon = "wrench"
    on = "failed"

    def process(self, context, plugin):

        ftrack_data = context.data["ftrackData"]
        task = ftrack.Task(ftrack_data["Task"]["id"])
        component_name = pyblish.api.current_host()

        asset = task.getParent().createAsset(
            task.getName(),
            "scene",
            task=task
        )

        file_path = os.path.join(tempfile.gettempdir(), "pyblish-tgbvfx.mb")
        pymel.core.system.saveAs(file_path)

        version = asset.createVersion(taskid=task.getId())
        component = version.createComponent(
            name=component_name, path=file_path
        )

        asset.publish()

        pymel.core.system.openFile(component.getFilesystemPath(), force=True)


class TGBVFXMayaValidateScene(pyblish.api.ContextPlugin):

    order = pyblish.api.ValidatorOrder
    label = "Scene"
    actions = [TGBVFXMayaRepairScene]
    hosts = ["maya"]

    def process(self, context):

        ftrack_data = context.data["ftrackData"]
        task = ftrack.Task(ftrack_data["Task"]["id"])
        component_name = pyblish.api.current_host()

        assets = task.getAssets(
            assetTypes=["scene"],
            names=[ftrack_data["Task"]["name"]],
            componentNames=[component_name]
        )

        if not assets:
            raise ValueError("No existing Ftrack asset found.")

        component = assets[0].getVersions()[-1].getComponent(
            name=component_name
        )

        current = context.data["currentFile"]
        expected = component.getFilesystemPath()
        msg = "Scene path is not correct. Current: \"{0}\" Expected: \"{1}\""
        assert expected == current, msg.format(current, expected)
